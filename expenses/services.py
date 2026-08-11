from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Expense, ExpenseShare


CENT = Decimal("0.01")


def as_money(value) -> Decimal:
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_equal_shares(total: Decimal, participant_ids) -> dict[int, Decimal]:
    """Split money exactly, assigning any remaining cents by ascending user id."""
    ids = sorted(int(value) for value in participant_ids)
    if not ids:
        return {}
    total_cents = int(as_money(total) * 100)
    base, remainder = divmod(total_cents, len(ids))
    return {
        user_id: Decimal(base + (1 if index < remainder else 0)) / 100
        for index, user_id in enumerate(ids)
    }


@transaction.atomic
def replace_expense_shares(expense: Expense, participants, custom_shares=None):
    existing = {share.user_id: share for share in expense.shares.all()}
    participant_list = list(participants)
    if custom_shares is None:
        amounts = calculate_equal_shares(expense.amount, [user.pk for user in participant_list])
    else:
        amounts = {int(user_id): as_money(amount) for user_id, amount in custom_shares.items()}

    expense.shares.all().delete()
    new_shares = []
    for user in participant_list:
        previous = existing.get(user.pk)
        payer_share = user.pk == expense.payer_id
        status = (
            ExpenseShare.Status.PAID
            if payer_share or (previous and previous.status == ExpenseShare.Status.PAID)
            else ExpenseShare.Status.UNPAID
        )
        paid_at = timezone.now() if payer_share and not previous else (previous.paid_at if previous else None)
        new_shares.append(
            ExpenseShare(
                expense=expense,
                user=user,
                amount=amounts[user.pk],
                status=status,
                paid_at=paid_at,
            )
        )
    ExpenseShare.objects.bulk_create(new_shares)


def expense_for_user(user, expense_id: int) -> Expense:
    return get_object_or_404(
        Expense.objects.filter(group__memberships__user=user).distinct()
        .select_related("group", "payer", "created_by")
        .prefetch_related("shares__user"),
        pk=expense_id,
    )
