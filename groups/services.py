from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import ExpenseGroup, GroupMembership


def group_for_user(user, group_id: int) -> ExpenseGroup:
    """Return a group visible to the user or raise a normal 404."""
    return get_object_or_404(
        ExpenseGroup.objects.filter(memberships__user=user).distinct(), pk=group_id
    )


def membership_for(user, group: ExpenseGroup) -> GroupMembership:
    return get_object_or_404(GroupMembership, group=group, user=user)


def require_admin(user, group: ExpenseGroup) -> GroupMembership:
    membership = membership_for(user, group)
    if membership.role != GroupMembership.Role.ADMIN:
        raise PermissionDenied("Group Admin access is required.")
    return membership


def user_has_unpaid_shares(user, group: ExpenseGroup) -> bool:
    from expenses.models import ExpenseShare

    return ExpenseShare.objects.filter(
        expense__group=group,
        user=user,
        status=ExpenseShare.Status.UNPAID,
    ).exists()


def group_has_unpaid_shares(group: ExpenseGroup) -> bool:
    from expenses.models import ExpenseShare

    return ExpenseShare.objects.filter(
        expense__group=group,
        status=ExpenseShare.Status.UNPAID,
    ).exists()
