from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from ..models import Project, Task, Session

User = get_user_model()

class SessionManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.project = Project.objects.create(user=self.user, name="Test Project")
        self.task = Task.objects.create(project=self.project, name="Test task")

    def test_get_active_session_returns_correct_session(self):
        # start time is set on task creation
        session = Session.objects.create(task=self.task)
        active_sesion = Session.objects.get_active_session(self.user)
        self.assertEqual(session, active_sesion)

    def test_get_active_session_returns_none_if_no_active_session(self):
        self.assertIsNone(Session.objects.get_active_session(self.user))

    def test_end_current_session_sets_endtime_to_active_session(self):
        session = Session.objects.create(task=self.task)
        Session.objects.end_current_session(self.user)
        session.refresh_from_db()
        self.assertIsNotNone(session.end_time)

    def test_create_new_session_creates_active_session(self):
        session = Session.objects.create_new_session(self.user, self.task)
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)

    def test_create_new_session_raises_error_if_another_session_is_active(self):
        session = Session.objects.create_new_session(user=self.user, task=self.task)
        with self.assertRaises(ValidationError):
            Session.objects.create_new_session(self.user, self.task)
        
    def test_start_project_and_start_date_within_returns_only_concerned_sessions(self):
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        
        yesterday_session = Session.objects.create(task=self.task)
        yesterday_session.start_time = yesterday
        yesterday_session.end_time = yesterday
        yesterday_session.save()

        today_session = Session.objects.create(task=self.task)
        today_session.set_start_time()
        today_session.set_end_time()
        today_session.save()

        today_sessions = Session.objects.by_user_and_start_date_within(self.user, now.date())

        self.assertIn(today_session, today_sessions)
        self.assertNotIn(yesterday_session, today_sessions)
        self.assertEqual(1, len(today_sessions))

        two_days_sessions = Session.objects.by_user_and_start_date_within(self.user, yesterday.date(), extra_days=1)
        self.assertIn(today_session, two_days_sessions)
        self.assertIn(yesterday_session, two_days_sessions)
        self.assertEqual(2, len(two_days_sessions))

class TaskManagerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.project = Project.objects.create(user=self.user, name="Test Project")

    def test_by_user_and_is_active(self):
        inactive_project = Project.objects.create(user=self.user, name="Inactive Project")
        inactive_project.active = False
        inactive_project.save()

        inactive_task = Task.objects.create(project=inactive_project, name="Pending inactive Task")

        pending_task = Task.objects.create(project=self.project, name="Pending active Task")
        done_task = Task.objects.create(project=self.project, name="Done active Task")
        done_task.is_done = True
        done_task.save()

        pending_active_tasks = Task.objects.by_user_and_is_active(user=self.user)
        self.assertIn(pending_task, pending_active_tasks)
        self.assertEqual(1, len(pending_active_tasks))

        done_active_tasks = Task.objects.by_user_and_is_active(user=self.user, is_done=True)
        self.assertIn(done_task, done_active_tasks)
        self.assertEqual(1, len(done_active_tasks))

    def test_by_user_and_done_date_within(self):
        now = timezone.now()
        yesterday = now - timedelta(days=1)

        done_today = Task.objects.create(project=self.project, name="Done today")
        done_today.is_done = True
        # on save, done_at is set to now if empty
        done_today.save()

        done_yesterday = Task.objects.create(project=self.project, name="Done yesterday")
        done_yesterday.is_done = True
        done_yesterday.done_at = yesterday
        done_yesterday.save()

        all_done_today = Task.objects.by_user_and_done_date_within(self.user, now.date())
        self.assertIn(done_today, all_done_today)
        self.assertEqual(1, len(all_done_today))

        all_done_two_days = Task.objects.by_user_and_done_date_within(self.user, yesterday.date(), extra_days=1)
        # make sure results are in correct order (descending done at)
        self.assertEqual(all_done_two_days[0], done_today)
        self.assertEqual(all_done_two_days[1], done_yesterday)
        self.assertEqual(2, len(all_done_two_days))
