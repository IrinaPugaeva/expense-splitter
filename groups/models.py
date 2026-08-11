from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def default_invitation_expiry():
    return timezone.now() + timedelta(days=7)


class ExpenseGroup(models.Model):
    class Category(models.TextChoices):
        HOUSEHOLD = "household", "Household"
        TRAVEL = "travel", "Travel"
        FOOD = "food", "Food"
        SHOPPING = "shopping", "Shopping"
        OTHER = "other", "Other"

    class SplitMethod(models.TextChoices):
        EQUAL = "equal", "Equal split"
        CUSTOM = "custom", "Custom split"

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.HOUSEHOLD)
    default_split = models.CharField(
        max_length=10, choices=SplitMethod.choices, default=SplitMethod.EQUAL
    )
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_expense_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class GroupMembership(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    group = models.ForeignKey(ExpenseGroup, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_group_memberships",
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("group", "user"), name="unique_expense_group_membership"
            )
        ]
        ordering = ("joined_at",)

    def __str__(self) -> str:
        return f"{self.user} — {self.group} ({self.get_role_display()})"


class GroupInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    group = models.ForeignKey(ExpenseGroup, on_delete=models.CASCADE, related_name="invitations")
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_invitations",
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_group_invitations",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    expires_at = models.DateTimeField(default=default_invitation_expiry)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    def __str__(self) -> str:
        return f"{self.invited_user} invited to {self.group}"
