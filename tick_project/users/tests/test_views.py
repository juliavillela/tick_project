from django.contrib.auth import get_user_model, get_user
from django.test import TestCase, Client
from django.urls import reverse

from tracker.models import Project

User = get_user_model()

class RegisterViewTest(TestCase):
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

class LoginViewTests(TestCase):
    def setUp(self):
        self.email = "user@example.com"
        self.password = "securepassword123"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )
        self.url = reverse("users:login")  # adjust if needed

    def test_login_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(self.url, {
            "username": self.email,
            "password": self.password,
        })

        # Check redirect
        self.assertRedirects(response, reverse("tracker:dashboard"))

        # Check user is logged in
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.email, self.email)

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(self.url, {
            "username": self.email,
            "password": "wrongpassword",
        })

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

        # User should not be logged in
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)