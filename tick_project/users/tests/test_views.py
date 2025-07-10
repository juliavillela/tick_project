from django.contrib.auth import get_user_model, get_user, authenticate
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
        self.url = reverse("users:login")

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

class UpdateEmailViewTests(TestCase):
    def setUp(self):
        self.email = "old@example.com"
        self.password = "Securepassword123"
        self.user = User.objects.create_user(
            email=self.email, password=self.password
        )
        self.url = reverse("users:update-email")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_get_form_when_logged_in(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")

    def test_post_valid_data_updates_email(self):
        new_email = "new@example.com"
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(self.url, {
            "email": new_email,
            "password": self.password 
        })
        # Refresh to get latest data from DB
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)
        self.assertRedirects(response, reverse("users:account"))

    def test_post_invalid_password_shows_errors(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(self.url, {
            "email": "new@example.com",
            "password": "wrongpassword"
        })

        # Should stay on form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")
        # Form should contain an error message for password field
        self.assertIn("password", response.context["form"].errors)

        # Email should not be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

    def test_post_invalid_email_shows_errors(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(self.url, {
            "email": "invalid-email",
            "password": self.password
        })

        # Should stay on form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")

        # Form should contain an error message for email field
        self.assertIn("email", response.context["form"].errors)

        # Email should not be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

class PasswordUpdateViewTests(TestCase):
    def setUp(self):
        self.email = "old@example.com"
        self.password = "Securepassword123"
        self.user = User.objects.create_user(
            email=self.email, password=self.password
        )
        self.url = reverse("users:update-password")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"/users/login/?next={self.url}")

    def test_get_form_when_logged_in(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")

    def test_post_valid_data_updates_password(self):
        self.client.login(email=self.email, password=self.password)
        new_password = "NewStrongPassword1"
        response = self.client.post(self.url, {
            "old_password": self.password,
            "new_password1": new_password,
            "new_password2": new_password
        })

        # Check that user can authenticate with new password
        user = authenticate(email=self.email, password=new_password)
        self.assertIsNotNone(user)
        self.assertEqual(self.user.pk, user.pk)

        # Should redirect the user to login page
        self.assertRedirects(response, reverse("users:login"))

    def test_post_with_wrong_password_shows_errors(self):
        self.client.login(email=self.email, password=self.password)
        new_password = "NewStrongPassword1"
        response = self.client.post(self.url, {
            "old_password": "wrongPassword",
            "new_password1": new_password,
            "new_password2": new_password
        })
        # Should stay on form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")
        # Form should contain an error message for old_password field
        self.assertIn("old_password", response.context["form"].errors)

    def test_post_with_mismatching_new_password_shows_errors(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.post(self.url, {
            "old_password": self.password,
            "new_password1": "NewStrongPassword1",
            "new_password2": "wrongNewPassword"
        })
        # Should stay on form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")
        # Form should contain an error message for new_password2 (password confimation) field
        self.assertIn("new_password2", response.context["form"].errors)

    def test_weak_new_password_shows_errors(self):
        self.client.login(email=self.email, password=self.password)
        weak_password = "12345"
        response = self.client.post(self.url, {
            "old_password": self.password,
            "new_password1": weak_password,
            "new_password2": weak_password
        })
        # Should stay on form page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_form.html")
        # Form should contain an error message for new_password2 field
        self.assertIn("new_password2", response.context["form"].errors)
