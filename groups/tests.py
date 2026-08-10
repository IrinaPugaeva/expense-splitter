from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ExpenseGroup, GroupMembership


class GroupAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="irina@torrens.edu.au",
            password="ExpenseMate123!",
            first_name="Irina",
        )
        self.other_user = get_user_model().objects.create_user(
            email="nicolas@torrens.edu.au",
            password="ExpenseMate123!",
            first_name="Nicolas",
        )

    def test_group_list_requires_authentication(self):
        response = self.client.get(reverse("group_list"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('group_list')}",
        )

    def test_group_create_requires_authentication(self):
        response = self.client.get(reverse("group_create"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('group_create')}",
        )

    def test_group_list_only_displays_memberships_for_signed_in_user(self):
        visible_group = ExpenseGroup.objects.create(
            title="Grocery",
            category=ExpenseGroup.Category.HOUSEHOLD,
            default_split=ExpenseGroup.SplitMethod.EQUAL,
            created_by=self.user,
        )
        hidden_group = ExpenseGroup.objects.create(
            title="Private trip",
            category=ExpenseGroup.Category.TRAVEL,
            default_split=ExpenseGroup.SplitMethod.EQUAL,
            created_by=self.other_user,
        )
        GroupMembership.objects.create(
            group=visible_group,
            user=self.user,
            role=GroupMembership.Role.ADMIN,
        )
        GroupMembership.objects.create(
            group=hidden_group,
            user=self.other_user,
            role=GroupMembership.Role.ADMIN,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("group_list"))

        self.assertContains(response, "Grocery")
        self.assertNotContains(response, "Private trip")


class GroupCreateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="irina@torrens.edu.au",
            password="ExpenseMate123!",
            first_name="Irina",
        )
        self.client.force_login(self.user)

    def test_create_group_creates_admin_membership(self):
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "Flatmates",
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
                "description": "Shared household expenses",
            },
        )

        group = ExpenseGroup.objects.get(title="Flatmates")
        membership = GroupMembership.objects.get(group=group, user=self.user)
        self.assertEqual(group.created_by, self.user)
        self.assertEqual(membership.role, GroupMembership.Role.ADMIN)
        self.assertRedirects(response, reverse("group_list"))

    def test_empty_title_is_rejected(self):
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "",
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
                "description": "Shared household expenses",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group title is required.")
        self.assertFalse(ExpenseGroup.objects.exists())

    def test_title_longer_than_100_characters_is_rejected(self):
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "A" * 101,
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
                "description": "Shared household expenses",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Group title must be 100 characters or fewer.")
        self.assertFalse(ExpenseGroup.objects.exists())
