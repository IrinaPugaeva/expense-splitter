from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from groups.models import ExpenseGroup, GroupMembership
from .models import Expense, ExpenseShare
from .services import calculate_equal_shares


class ExpenseFeatureTests(TestCase):
    password = "Password1234"

    def setUp(self):
        user_model = get_user_model()
        self.irina = user_model.objects.create_user(
            email="irina@test.com",
            password=self.password,
            first_name="Irina",
            payid="irina@payid.bank",
        )
        self.nicolas = user_model.objects.create_user(
            email="nicolas@test.com", password=self.password, first_name="Nicolas"
        )
        self.jobaida = user_model.objects.create_user(
            email="jobaida@test.com", password=self.password, first_name="Jobaida"
        )
        self.samesh = user_model.objects.create_user(
            email="samesh@test.com", password=self.password, first_name="Samesh"
        )
        self.group = ExpenseGroup.objects.create(
            title="Flatmates",
            description="Shared household costs",
            category=ExpenseGroup.Category.HOUSEHOLD,
            default_split=ExpenseGroup.SplitMethod.EQUAL,
            created_by=self.irina,
        )
        for user, role in [
            (self.irina, GroupMembership.Role.ADMIN),
            (self.nicolas, GroupMembership.Role.MEMBER),
            (self.jobaida, GroupMembership.Role.MEMBER),
            (self.samesh, GroupMembership.Role.MEMBER),
        ]:
            GroupMembership.objects.create(group=self.group, user=user, role=role)

    def valid_data(self, **overrides):
        data = {
            "title": "Dinner",
            "amount": "60.00",
            "date": str(timezone.localdate()),
            "category": Expense.Category.FOOD,
            "description": "Dinner after class",
            "due_date": str(timezone.localdate() + timedelta(days=3)),
            "payer": str(self.irina.pk),
            "participants": [str(self.irina.pk), str(self.nicolas.pk), str(self.jobaida.pk)],
            "split_method": Expense.SplitMethod.EQUAL,
        }
        data.update(overrides)
        return data

    def create_expense(self, *, due_date=None):
        expense = Expense.objects.create(
            group=self.group,
            title="Dinner",
            amount=Decimal("60.00"),
            date=timezone.localdate(),
            category=Expense.Category.FOOD,
            description="Dinner after class",
            due_date=due_date or timezone.localdate() + timedelta(days=3),
            payer=self.irina,
            split_method=Expense.SplitMethod.EQUAL,
            created_by=self.irina,
        )
        ExpenseShare.objects.bulk_create(
            [
                ExpenseShare(
                    expense=expense,
                    user=self.irina,
                    amount=Decimal("20.00"),
                    status=ExpenseShare.Status.PAID,
                ),
                ExpenseShare(
                    expense=expense,
                    user=self.nicolas,
                    amount=Decimal("20.00"),
                    status=ExpenseShare.Status.UNPAID,
                ),
                ExpenseShare(
                    expense=expense,
                    user=self.jobaida,
                    amount=Decimal("20.00"),
                    status=ExpenseShare.Status.PAID,
                ),
            ]
        )
        return expense

    def test_equal_split_distributes_all_cents(self):
        shares = calculate_equal_shares(Decimal("100.00"), [3, 1, 2])
        self.assertEqual(sum(shares.values()), Decimal("100.00"))
        self.assertEqual(shares[1], Decimal("33.34"))
        self.assertEqual(shares[2], Decimal("33.33"))
        self.assertEqual(shares[3], Decimal("33.33"))

    def test_member_can_add_expense_with_payer_participants_and_equal_split(self):
        self.client.force_login(self.nicolas)
        response = self.client.post(reverse("expense_create", args=[self.group.pk]), self.valid_data())
        expense = Expense.objects.get(title="Dinner")
        self.assertRedirects(response, reverse("expense_detail", args=[expense.pk]))
        self.assertEqual(expense.payer, self.irina)
        self.assertEqual(expense.shares.count(), 3)
        self.assertFalse(expense.shares.filter(user=self.samesh).exists())
        self.assertEqual(expense.shares.get(user=self.irina).status, ExpenseShare.Status.PAID)
        self.assertEqual(expense.shares.get(user=self.nicolas).amount, Decimal("20.00"))

    def test_custom_split_is_saved(self):
        self.client.force_login(self.irina)
        data = self.valid_data(
            amount="100.00",
            participants=[str(self.irina.pk), str(self.nicolas.pk)],
            split_method=Expense.SplitMethod.CUSTOM,
        )
        data[f"share_{self.irina.pk}"] = "70.00"
        data[f"share_{self.nicolas.pk}"] = "30.00"
        response = self.client.post(reverse("expense_create", args=[self.group.pk]), data)
        expense = Expense.objects.get(title="Dinner")
        self.assertRedirects(response, reverse("expense_detail", args=[expense.pk]))
        self.assertEqual(expense.shares.get(user=self.irina).amount, Decimal("70.00"))
        self.assertEqual(expense.shares.get(user=self.nicolas).amount, Decimal("30.00"))

    def test_custom_split_must_equal_total(self):
        self.client.force_login(self.irina)
        data = self.valid_data(
            amount="100.00",
            participants=[str(self.irina.pk), str(self.nicolas.pk)],
            split_method=Expense.SplitMethod.CUSTOM,
        )
        data[f"share_{self.irina.pk}"] = "80.00"
        data[f"share_{self.nicolas.pk}"] = "10.00"
        response = self.client.post(reverse("expense_create", args=[self.group.pk]), data)
        self.assertContains(response, "Shares must total AUD 100.00")
        self.assertFalse(Expense.objects.exists())

    def test_custom_split_rejects_negative_share(self):
        self.client.force_login(self.irina)
        data = self.valid_data(
            amount="100.00",
            participants=[str(self.irina.pk), str(self.nicolas.pk)],
            split_method=Expense.SplitMethod.CUSTOM,
        )
        data[f"share_{self.irina.pk}"] = "110.00"
        data[f"share_{self.nicolas.pk}"] = "-10.00"
        response = self.client.post(reverse("expense_create", args=[self.group.pk]), data)
        self.assertContains(response, "Share amounts cannot be negative")
        self.assertFalse(Expense.objects.exists())

    def test_missing_title_is_rejected(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_create", args=[self.group.pk]), self.valid_data(title="")
        )
        self.assertContains(response, "Expense title is required")
        self.assertFalse(Expense.objects.exists())

    def test_negative_and_zero_amount_are_rejected(self):
        self.client.force_login(self.irina)
        for amount in ["-50.00", "0.00"]:
            response = self.client.post(
                reverse("expense_create", args=[self.group.pk]), self.valid_data(amount=amount)
            )
            self.assertContains(response, "Amount must be greater than 0")
        self.assertFalse(Expense.objects.exists())

    def test_all_required_expense_fields_are_validated(self):
        self.client.force_login(self.irina)
        for field in ["amount", "date", "category", "description", "due_date"]:
            response = self.client.post(
                reverse("expense_create", args=[self.group.pk]), self.valid_data(**{field: ""})
            )
            self.assertContains(response, "This field is required")
        self.assertFalse(Expense.objects.exists())

    def test_payer_is_required(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_create", args=[self.group.pk]), self.valid_data(payer="")
        )
        self.assertContains(response, "Select a payer")

    def test_at_least_one_participant_is_required(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_create", args=[self.group.pk]), self.valid_data(participants=[])
        )
        self.assertContains(response, "Select at least one participant")

    def test_due_date_cannot_be_before_expense_date(self):
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_create", args=[self.group.pk]),
            self.valid_data(due_date=str(timezone.localdate() - timedelta(days=1))),
        )
        self.assertContains(response, "Due date cannot be earlier than the expense date")

    def test_duplicate_expense_is_rejected(self):
        self.create_expense()
        self.client.force_login(self.irina)
        response = self.client.post(reverse("expense_create", args=[self.group.pk]), self.valid_data())
        self.assertContains(response, "An identical expense already exists")
        self.assertEqual(Expense.objects.count(), 1)

    def test_admin_can_edit_expense_and_member_cannot(self):
        expense = self.create_expense()
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_edit", args=[expense.pk]),
            self.valid_data(title="Updated dinner", amount="90.00"),
        )
        expense.refresh_from_db()
        self.assertEqual(expense.title, "Updated dinner")
        self.assertEqual(expense.amount, Decimal("90.00"))
        self.client.force_login(self.nicolas)
        self.assertEqual(self.client.get(reverse("expense_edit", args=[expense.pk])).status_code, 403)
        detail = self.client.get(reverse("expense_detail", args=[expense.pk]))
        self.assertNotContains(detail, "Edit expense")

    def test_admin_can_delete_expense_and_member_cannot(self):
        expense = self.create_expense()
        self.client.force_login(self.nicolas)
        self.assertEqual(self.client.post(reverse("expense_delete", args=[expense.pk])).status_code, 403)
        detail = self.client.get(reverse("expense_detail", args=[expense.pk]))
        self.assertNotContains(detail, "Delete expense")
        self.client.force_login(self.irina)
        response = self.client.post(reverse("expense_delete", args=[expense.pk]))
        self.assertRedirects(response, reverse("expense_list", args=[self.group.pk]))
        self.assertFalse(Expense.objects.filter(pk=expense.pk).exists())

    def test_admin_can_correct_split_and_negative_split_is_rejected(self):
        expense = self.create_expense()
        self.client.force_login(self.irina)
        response = self.client.post(
            reverse("expense_split_correct", args=[expense.pk]),
            {
                f"share_{self.irina.pk}": "10.00",
                f"share_{self.nicolas.pk}": "30.00",
                f"share_{self.jobaida.pk}": "20.00",
            },
        )
        self.assertRedirects(response, reverse("expense_detail", args=[expense.pk]))
        self.assertEqual(expense.shares.get(user=self.nicolas).amount, Decimal("30.00"))
        response = self.client.post(
            reverse("expense_split_correct", args=[expense.pk]),
            {
                f"share_{self.irina.pk}": "70.00",
                f"share_{self.nicolas.pk}": "-10.00",
                f"share_{self.jobaida.pk}": "0.00",
            },
        )
        self.assertContains(response, "Share amounts cannot be negative")

    def test_expense_list_filters_by_title_category_and_date(self):
        expense = self.create_expense()
        Expense.objects.create(
            group=self.group,
            title="Electricity bill",
            amount=Decimal("120.00"),
            date=timezone.localdate() - timedelta(days=30),
            category=Expense.Category.UTILITIES,
            description="Monthly electricity",
            due_date=timezone.localdate() - timedelta(days=20),
            payer=self.irina,
            split_method=Expense.SplitMethod.EQUAL,
            created_by=self.irina,
        )
        self.client.force_login(self.irina)
        response = self.client.get(
            reverse("expense_list", args=[self.group.pk]),
            {
                "title": "Dinner",
                "category": Expense.Category.FOOD,
                "date_from": str(timezone.localdate()),
                "date_to": str(timezone.localdate()),
            },
        )
        self.assertContains(response, expense.title)
        self.assertNotContains(response, "Electricity bill")

    def test_expense_detail_displays_all_fields_shares_and_statuses(self):
        expense = self.create_expense()
        self.client.force_login(self.nicolas)
        response = self.client.get(reverse("expense_detail", args=[expense.pk]))
        self.assertContains(response, "Dinner")
        self.assertContains(response, "Paid by Irina")
        self.assertContains(response, "AUD 20.00")
        self.assertContains(response, "Unpaid")
        self.assertContains(response, "irina@payid.bank")
        self.assertContains(response, "Copy PayID")

    def test_participant_can_mark_share_paid_but_payer_cannot(self):
        expense = self.create_expense()
        self.client.force_login(self.nicolas)
        response = self.client.post(reverse("expense_mark_paid", args=[expense.pk]))
        self.assertRedirects(response, reverse("expense_detail", args=[expense.pk]))
        share = expense.shares.get(user=self.nicolas)
        self.assertEqual(share.status, ExpenseShare.Status.PAID)
        self.client.force_login(self.irina)
        detail = self.client.get(reverse("expense_detail", args=[expense.pk]))
        self.assertNotContains(detail, "Mark as paid")
        response = self.client.post(reverse("expense_mark_paid", args=[expense.pk]))
        self.assertEqual(response.status_code, 400)

    def test_payment_reminder_status_changes_for_tomorrow_and_overdue(self):
        tomorrow = self.create_expense(due_date=timezone.localdate() + timedelta(days=1))
        share = tomorrow.shares.get(user=self.nicolas)
        self.assertEqual(share.display_status, "Payment due tomorrow")
        tomorrow.due_date = timezone.localdate() - timedelta(days=1)
        tomorrow.save(update_fields=["due_date"])
        share.refresh_from_db()
        self.assertEqual(share.display_status, "Overdue")

    def test_non_member_cannot_view_group_expenses(self):
        outsider = get_user_model().objects.create_user(
            email="outsider@test.com", password=self.password
        )
        expense = self.create_expense()
        self.client.force_login(outsider)
        self.assertEqual(self.client.get(reverse("expense_detail", args=[expense.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("expense_list", args=[self.group.pk])).status_code, 404)
