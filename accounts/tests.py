from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="irina@torrens.edu.au",
            password="ExpenseMate123!",
            first_name="Irina",
        )

    def test_valid_email_and_password_redirect_to_group_list(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.email, "password": "ExpenseMate123!"},
        )

        self.assertRedirects(response, reverse("group_list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_invalid_password_displays_generic_error(self):
        response = self.client.post(
            reverse("login"),
            {"username": self.user.email, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password. Please try again.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_user_visiting_login_is_redirected(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("login"))

        self.assertRedirects(response, reverse("group_list"))
