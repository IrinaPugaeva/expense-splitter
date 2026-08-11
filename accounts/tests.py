from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountFeatureTests(TestCase):
    password = "Password1234"

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="irina@test.com",
            password=self.password,
            first_name="Irina",
        )

    def test_registration_creates_account_logs_in_and_opens_empty_dashboard(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "New Irina",
                "email": "irina.new@test.com",
                "password1": "Password1234",
                "password2": "Password1234",
            },
        )
        new_user = get_user_model().objects.get(email="irina.new@test.com")
        self.assertRedirects(response, reverse("group_list"))
        self.assertEqual(new_user.first_name, "New Irina")
        self.assertEqual(int(self.client.session["_auth_user_id"]), new_user.pk)

    def test_registration_rejects_invalid_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "Irina",
                "email": "irina@",
                "password1": "Password1234",
                "password2": "Password1234",
            },
        )
        self.assertContains(response, "Enter a valid email address")
        self.assertFalse(get_user_model().objects.filter(email="irina@").exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "Irina",
                "email": "irina.new@test.com",
                "password1": "Pass1",
                "password2": "Pass1",
            },
        )
        self.assertContains(response, "This password is too short")
        self.assertFalse(get_user_model().objects.filter(email="irina.new@test.com").exists())

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "Irina",
                "email": "irina.new@test.com",
                "password1": "Password1234",
                "password2": "Password1235",
            },
        )
        self.assertContains(response, "Passwords do not match")

    def test_registration_rejects_duplicate_account(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "Irina Two",
                "email": "irina@test.com",
                "password1": "Password1234",
                "password2": "Password1234",
            },
        )
        self.assertContains(response, "Account with this email already exists")
        self.assertEqual(get_user_model().objects.filter(email="irina@test.com").count(), 1)

    def test_registration_requires_name(self):
        response = self.client.post(
            reverse("register"),
            {
                "name": "",
                "email": "irina.new@test.com",
                "password1": "Password1234",
                "password2": "Password1234",
            },
        )
        self.assertContains(response, "Name is required")

    def test_valid_login_redirects_to_group_list(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": self.password},
        )
        self.assertRedirects(response, reverse("group_list"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_wrong_password_displays_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": "Password9999"},
        )
        self.assertContains(response, "Invalid credentials")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_email_displays_no_account_found(self):
        response = self.client.post(
            reverse("login"),
            {"email": "unknown@test.com", "password": self.password},
        )
        self.assertContains(response, "No account found")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_reset_updates_password(self):
        response = self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertRedirects(response, reverse("password_reset_confirm"))
        response = self.client.post(
            reverse("password_reset_confirm"),
            {"password1": "Password5678", "password2": "Password5678"},
        )
        self.assertRedirects(response, reverse("login"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Password5678"))

    def test_password_reset_rejects_unknown_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "unknown@test.com"})
        self.assertContains(response, "No account found")

    def test_profile_updates_payid(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("profile"),
            {"first_name": "Irina", "payid": "irina@payid.bank"},
        )
        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.payid, "irina@payid.bank")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")
