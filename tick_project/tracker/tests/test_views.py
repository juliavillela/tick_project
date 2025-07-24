from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Project, Task, Session

User = get_user_model()

class AuthenticatedViewMixin:
    def setUp(self):
        self.email = "test@example.com"
        self.password = "StrongPassword123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

        self.project = Project.objects.create(
            user=self.user,
            name="General"
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_returns_200_and_uses_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

class TestTaskListView(AuthenticatedViewMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("tracker:tasks")
        self.template = "task_list.html"

    def test_list_view_get(self):
        pending_task = Task.objects.create(project=self.project, name="Pending task")
        done_task = Task.objects.create(project=self.project, name="Done task", is_done=True)
        
        response = self.client.get(self.url)
        context = response.context

        self.assertIn(pending_task, context["pending_tasks"])
        self.assertIn(done_task, context["done_tasks"])

class TestTaskDetailView(AuthenticatedViewMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            project = self.project,
            name="Test task"
        )
        self.url = reverse("tracker:task-detail", kwargs={"pk": self.task.pk})
        self.template = "task_detail.html"

    def test_detail_view_context(self):
        session = Session.objects.create(
            task = self.task
        )
        response = self.client.get(self.url)
        context = response.context

        self.assertIn(session, context["sessions"])
        self.assertEqual(len(context["sessions"]), 1)

class DailyViewTest(AuthenticatedViewMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("tracker:daily", kwargs={"days_ago": 0})
        self.template = "daily.html"

        self.task = Task.objects.create(
            project = self.project,
            name = "Test task"
        )
    def test_get_daily_view_context(self):
        # create a 30 min session for today
        start_time = timezone.now() - timedelta(minutes=30)
        end_time = timezone.now()
        today_session_1 = Session.objects.create(
            task = self.task,
            start_time = start_time,
            end_time = end_time
        )
        
        response = self.client.get(self.url)
        context = response.context

        self.assertIn(self.project, context["projects"])
        self.assertIn(today_session_1, context["sessions"])
        self.assertEqual(len(context["sessions"]), 1)
        self.assertEqual(context["daily_time"], {"hours":0, "minutes":30})
