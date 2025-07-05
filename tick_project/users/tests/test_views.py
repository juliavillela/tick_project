from django.contrib.auth import get_user_model, get_user
from django.test import TestCase, Client
from django.urls import reverse

from tracker.models import Project

User = get_user_model()

class RegisterViewTeste(TestCase):
    def setUp(self):
        self.url = reverse("users:register")  
        self.default_project_name = "General"
        self.valid_user_data = {
            "email": "newuser@example.com",
            "password1": "Strongpassword123",
            "password2": "Strongpassword123",
        }
    
    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_view_post_valid_data_creates_user_and_project(self):
        response = self.client.post(self.url, self.valid_user_data)

        # Check user created
        user = User.objects.get(email=self.valid_user_data["email"])
        self.assertIsNotNone(user)

        # Check user is logged in
        logged_user = get_user(self.client)
        self.assertEqual(logged_user, user)

        # Check a project was created for the user
        projects = Project.objects.filter(user=user)
        self.assertEqual(len(projects), 1)

        # Check redirect
        self.assertRedirects(response, reverse("tracker:dashboard"))
