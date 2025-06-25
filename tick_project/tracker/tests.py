from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Project, Task, Session

User = get_user_model()

class ProjectModelTests(TestCase):
    def setUp(self):
        # Create a user for associating with project
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

    def test_project_creation(self):
        project = Project.objects.create(user=self.user, name="Test Project")
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.user, self.user)
        self.assertEqual(project.color, "#C3C3C3")  # default color
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.last_edited)

    def test_project_str(self):
        project = Project.objects.create(user=self.user, name="My Project")
        self.assertEqual(str(project), "My Project")

    def test_project_color_custom(self):
        project = Project.objects.create(user=self.user, name="Colored Project", color="#FF0000")
        self.assertEqual(project.color, "#FF0000")

    def test_total_time_spent(self):
        project = Project.objects.create(user=self.user, name="My Project")

        # Create two tasks in the project
        task1 = Task.objects.create(project=project, name="Task 1")
        task2 = Task.objects.create(project=project, name="Task 2")
        
        # Mock total_time_spent for tasks by creating sessions with known durations
        start = timezone.now() 
        end = start + timedelta(seconds=30)
        session_1 = Session.objects.create(task=task1, start_time=start, end_time=end)

        start = end
        end = end + timedelta(seconds=30)
        session_2 = Session.objects.create(task=task2, start_time=start, end_time=end)

        self.assertEqual(project.total_time_spent(), 60)

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.project = Project.objects.create(user=self.user, name="Test Project")

    def test_task_creation(self):
        task = Task.objects.create(project=self.project, name="Test Task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(self.project, task.project)
        self.assertFalse(task.is_done)
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.last_edited)

    def test_task_str(self):
        task = Task.objects.create(project=self.project, name="Test Task")
        self.assertEqual(f"{task.name} - {self.project}", task.__str__())

    def test_total_time_spent(self):
        task = Task.objects.create(project=self.project, name="Test Task")

        start = timezone.now() 
        end = start + timedelta(seconds=30)
        session_1 = Session.objects.create(task=task, start_time=start, end_time=end)

        start = end
        end = end + timedelta(seconds=30)
        session_2 = Session.objects.create(task=task, start_time=start, end_time=end)

        self.assertEqual(task.total_time_spent(), 60)


class SessionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.project = Project.objects.create(user=self.user, name="Test Project")
        self.task = Task.objects.create(project=self.project, name="Test Task")

    def test_session_creation(self):
        session = Session.objects.create(task=self.task)

        self.assertEqual(session.task, self.task)
        self.assertIsNone(session.start_time)
        self.assertIsNone(session.end_time)

    def test_set_start_and_end_time(self):
        session = Session.objects.create(task=self.task)

        session.set_start_time()
        self.assertIsNotNone(session.start_time)

        session.set_end_time()
        self.assertIsNotNone(session.end_time)


    def test_duration_in_seconds(self):
        start = timezone.now() 
        end = start + timedelta(seconds=30)
        session = Session.objects.create(task=self.task, start_time=start, end_time=end)
        self.assertEqual(session.duration_in_seconds(), 30)

        #raise error if one of the timestamps are missing
        session.end_time = None
        with self.assertRaises(TypeError):
            session.duration_in_seconds()
