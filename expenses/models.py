from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from groups.models import ExpenseGroup


class Expense(models.Model):
    class Category(models.TextChoices):
        FOOD = "food", "Food"
        UTILITIES = "utilities", "Utilities"
        RENT = "rent", "Rent"
        TRAVEL = "travel", "Travel"
        SHOPPING = "shopping", "Shopping"
        OTHER = "other", "Other"

    class SplitMethod(models.TextChoices):
        EQUAL = "equal", "Equal"
        CUSTOM = "custom", "Custom"

    group = models.ForeignKey(ExpenseGroup, on_delete=models.CASCADE, related_name="expenses")
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField()
    due_date = models.DateField()
    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="paid_expenses",
    )
    split_method = models.CharField(
        max_length=10, choices=SplitMethod.choices, default=SplitMethod.EQUAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-date", "-created_at")

    @property
    def is_settled(self) -> bool:
        return not self.shares.filter(status=ExpenseShare.Status.UNPAID).exists()

    def __str__(self) -> str:
        return f"{self.title} — AUD {self.amount}"


class ExpenseShare(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PAID = "paid", "Paid"

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name="shares")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_shares",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("expense", "user"), name="unique_expense_participant_share"
            )
        ]
        ordering = ("user_id",)

    @property
    def display_status(self) -> str:
        if self.status == self.Status.PAID:
            return "Paid"
        today = timezone.localdate()
        if self.expense.due_date < today:
            return "Overdue"
        if self.expense.due_date == today + timedelta(days=1):
            return "Payment due tomorrow"
        return "Unpaid"

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])

    def __str__(self) -> str:
        return f"{self.user}: AUD {self.amount} ({self.display_status})"
