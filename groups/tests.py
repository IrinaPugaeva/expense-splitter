from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from expenses.models import Expense, ExpenseShare
from .models import ExpenseGroup, GroupInvitation, GroupMembership


class GroupFeatureTests(TestCase):
    password = "Password1234"

    def setUp(self):
        user_model = get_user_model()
        self.irina = user_model.objects.create_user(
            email="irina@test.com", password=self.password, first_name="Irina"
        )
        self.nicolas = user_model.objects.create_user(
            email="nicolas@test.com", password=self.password, first_name="Nicolas"
        )
        self.jobaida = user_model.objects.create_user(
            email="jobaida@test.com", password=self.password, first_name="Jobaida"
        )
        self.group = ExpenseGroup.objects.create(
            title="Flatmates",
            description="Shared household costs",
            category=ExpenseGroup.Category.HOUSEHOLD,
            default_split=ExpenseGroup.SplitMethod.EQUAL,
            created_by=self.irina,
        )
        self.admin_membership = GroupMembership.objects.create(
            group=self.group, user=self.irina, role=GroupMembership.Role.ADMIN
        )
        self.member_membership = GroupMembership.objects.create(
            group=self.group, user=self.nicolas, role=GroupMembership.Role.MEMBER
        )

    def create_expense_with_share(self, user, paid=False):
        expense = Expense.objects.create(
            group=self.group,
            title="Dinner",
            amount=Decimal("100.00"),
            date=timezone.localdate(),
            category=Expense.Category.FOOD,
            description="Dinner after class",
            due_date=timezone.localdate() + timedelta(days=2),
            payer=self.irina,
            split_method=Expense.SplitMethod.EQUAL,
            created_by=self.irina,
        )
        ExpenseShare.objects.create(
            expense=expense,
            user=self.irina,
            amount=Decimal("50.00"),
            status=ExpenseShare.Status.PAID,
        )
        ExpenseShare.objects.create(
            expense=expense,
            user=user,
            amount=Decimal("50.00"),
            status=ExpenseShare.Status.PAID if paid else ExpenseShare.Status.UNPAID,
        )
        return expense

    def test_create_group_assigns_creator_as_admin(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "Study trip",
                "description": "Course travel costs",
                "category": ExpenseGroup.Category.TRAVEL,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
            },
        )
        new_group = ExpenseGroup.objects.get(title="Study trip")
        membership = GroupMembership.objects.get(group=new_group, user=self.irina)
        self.assertEqual(membership.role, GroupMembership.Role.ADMIN)
        self.assertRedirects(response, reverse("group_detail", args=[new_group.pk]))

    def test_create_group_rejects_duplicate_title_for_same_user(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "flatmates",
                "description": "Duplicate",
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
            },
        )
        self.assertContains(response, "A group with this title already exists")
        self.assertEqual(ExpenseGroup.objects.filter(created_by=self.irina).count(), 1)

    def test_create_group_requires_title_and_description(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_create"),
            {
                "title": "",
                "description": "",
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
            },
        )
        self.assertContains(response, "Group title is required")
        self.assertContains(response, "Group description is required")

    def test_group_list_only_contains_groups_for_current_user(self):
        other = ExpenseGroup.objects.create(
            title="Private",
            description="Hidden",
            created_by=self.jobaida,
        )
        GroupMembership.objects.create(
            group=other, user=self.jobaida, role=GroupMembership.Role.ADMIN
        )
        self.client.force_login(self.irina)
        response = self.client.get(reverse("group_list"))
        self.assertContains(response, "Flatmates")
        self.assertNotContains(response, "Private")

    def test_group_detail_shows_title_members_roles_and_expenses(self):
        self.create_expense_with_share(self.nicolas)
        self.client.force_login(self.irina)
        response = self.client.get(reverse("group_detail", args=[self.group.pk]))
        self.assertContains(response, "Flatmates")
        self.assertContains(response, "Irina")
        self.assertContains(response, "Nicolas")
        self.assertContains(response, "Admin")
        self.assertContains(response, "Dinner")

    def test_admin_can_edit_group(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_edit", args=[self.group.pk]),
            {
                "title": "Flatmates updated",
                "description": "Updated information",
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
            },
        )
        self.group.refresh_from_db()
        self.assertEqual(self.group.title, "Flatmates updated")
        self.assertRedirects(response, reverse("group_detail", args=[self.group.pk]))

    def test_member_cannot_edit_group(self):
        self.client.force_login(self.nicolas)
        response = self.client.get(reverse("group_edit", args=[self.group.pk]))
        self.assertEqual(response.status_code, 403)
        detail = self.client.get(reverse("group_detail", args=[self.group.pk]))
        self.assertNotContains(detail, "Edit group")

    def test_admin_can_delete_group_when_all_shares_are_paid(self):
        self.create_expense_with_share(self.nicolas, paid=True)
        self.client.force_login(self.irina)
        response = self.client.post(reverse("group_delete", args=[self.group.pk]))
        self.assertRedirects(response, reverse("group_list"))
        self.assertFalse(ExpenseGroup.objects.filter(pk=self.group.pk).exists())

    def test_group_with_unpaid_expense_cannot_be_deleted(self):
        self.create_expense_with_share(self.nicolas, paid=False)
        self.client.force_login(self.irina)
        response = self.client.post(reverse("group_delete", args=[self.group.pk]))
        self.assertContains(response, "All expenses must be settled")
        self.assertTrue(ExpenseGroup.objects.filter(pk=self.group.pk).exists())

    def test_member_cannot_delete_group_or_see_delete_control(self):
        self.client.force_login(self.nicolas)
        response = self.client.post(reverse("group_delete", args=[self.group.pk]))
        self.assertEqual(response.status_code, 403)
        detail = self.client.get(reverse("group_detail", args=[self.group.pk]))
        self.assertNotContains(detail, "Delete group")

    def test_admin_invites_registered_user(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_invite", args=[self.group.pk]),
            {"email": self.jobaida.email},
        )
        invitation = GroupInvitation.objects.get(group=self.group, invited_user=self.jobaida)
        self.assertEqual(invitation.status, GroupInvitation.Status.PENDING)
        self.assertRedirects(response, reverse("group_members", args=[self.group.pk]))

    def test_invitation_rejects_unknown_email(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_invite", args=[self.group.pk]),
            {"email": "unknown@test.com"},
        )
        self.assertContains(response, "User not found")
        self.assertFalse(GroupInvitation.objects.filter(group=self.group).exists())

    def test_invitation_rejects_existing_pending_invitation(self):
        GroupInvitation.objects.create(
            group=self.group,
            invited_user=self.jobaida,
            invited_by=self.irina,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_invite", args=[self.group.pk]),
            {"email": self.jobaida.email},
        )
        self.assertContains(response, "Already invited")
        self.assertEqual(GroupInvitation.objects.filter(group=self.group).count(), 1)

    def test_invitation_rejects_existing_member(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_invite", args=[self.group.pk]),
            {"email": self.nicolas.email},
        )
        self.assertContains(response, "Already a member")

    def test_invited_user_can_accept_invitation(self):
        invitation = GroupInvitation.objects.create(
            group=self.group,
            invited_user=self.jobaida,
            invited_by=self.irina,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_login(self.jobaida)
        response = self.client.post(reverse("invitation_accept", args=[invitation.pk]))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, GroupInvitation.Status.ACCEPTED)
        self.assertTrue(GroupMembership.objects.filter(group=self.group, user=self.jobaida).exists())
        self.assertRedirects(response, reverse("group_detail", args=[self.group.pk]))

    def test_invited_user_can_decline_invitation(self):
        invitation = GroupInvitation.objects.create(
            group=self.group,
            invited_user=self.jobaida,
            invited_by=self.irina,
            expires_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_login(self.jobaida)
        response = self.client.post(reverse("invitation_decline", args=[invitation.pk]))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, GroupInvitation.Status.DECLINED)
        self.assertFalse(GroupMembership.objects.filter(group=self.group, user=self.jobaida).exists())
        self.assertRedirects(response, reverse("group_list"))

    def test_expired_invitation_cannot_be_accepted(self):
        invitation = GroupInvitation.objects.create(
            group=self.group,
            invited_user=self.jobaida,
            invited_by=self.irina,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.client.force_login(self.jobaida)
        response = self.client.post(reverse("invitation_accept", args=[invitation.pk]))
        self.assertContains(response, "Invitation no longer valid", status_code=400)
        self.assertFalse(GroupMembership.objects.filter(group=self.group, user=self.jobaida).exists())

    def test_member_can_leave_when_all_own_shares_are_paid(self):
        self.create_expense_with_share(self.nicolas, paid=True)
        self.client.force_login(self.nicolas)
        response = self.client.post(reverse("group_leave", args=[self.group.pk]))
        self.assertRedirects(response, reverse("group_list"))
        self.assertFalse(GroupMembership.objects.filter(group=self.group, user=self.nicolas).exists())

    def test_member_cannot_leave_with_unpaid_share(self):
        self.create_expense_with_share(self.nicolas, paid=False)
        self.client.force_login(self.nicolas)
        response = self.client.post(reverse("group_leave", args=[self.group.pk]))
        self.assertContains(response, "Pay all shares first")
        self.assertTrue(GroupMembership.objects.filter(group=self.group, user=self.nicolas).exists())

    def test_admin_can_remove_member_without_unpaid_share(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_remove_member", args=[self.group.pk, self.member_membership.pk])
        )
        self.assertRedirects(response, reverse("group_members", args=[self.group.pk]))
        self.assertFalse(GroupMembership.objects.filter(pk=self.member_membership.pk).exists())

    def test_admin_cannot_remove_member_with_unpaid_share(self):
        self.create_expense_with_share(self.nicolas, paid=False)
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("group_remove_member", args=[self.group.pk, self.member_membership.pk])
        )
        self.assertContains(response, "Member has unpaid obligations")
        self.assertTrue(GroupMembership.objects.filter(pk=self.member_membership.pk).exists())

    def test_member_cannot_manage_membership(self):
        self.client.force_login(self.nicolas)
        response = self.client.post(
            reverse("group_invite", args=[self.group.pk]), {"email": self.jobaida.email}
        )
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
            reverse("group_remove_member", args=[self.group.pk, self.member_membership.pk])
        )
        self.assertEqual(response.status_code, 403)
        page = self.client.get(reverse("group_members", args=[self.group.pk]))
        self.assertNotContains(page, "Invite member")
        self.assertNotContains(page, "Remove")
