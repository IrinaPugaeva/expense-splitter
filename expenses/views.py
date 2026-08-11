from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

from groups.models import GroupMembership
from groups.services import group_for_user, membership_for, require_admin
from .forms import ExpenseForm, ExpenseSearchForm, SplitCorrectionForm
from .models import ExpenseShare
from .services import expense_for_user


@login_required
def expense_list(request, group_id):
    group = group_for_user(request.user, group_id)
    membership = membership_for(request.user, group)
    form = ExpenseSearchForm(request.GET or None)
    expenses = group.expenses.select_related("payer").prefetch_related("shares")
    if form.is_valid():
        title = form.cleaned_data.get("title")
        category = form.cleaned_data.get("category")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        if title:
            expenses = expenses.filter(title__icontains=title)
        if category:
            expenses = expenses.filter(category=category)
        if date_from:
            expenses = expenses.filter(date__gte=date_from)
        if date_to:
            expenses = expenses.filter(date__lte=date_to)
    return render(
        request,
        "expenses/expense_list.html",
        {"group": group, "membership": membership, "form": form, "expenses": expenses},
    )


@login_required
def expense_create(request, group_id):
    group = group_for_user(request.user, group_id)
    membership_for(request.user, group)
    initial = {"split_method": group.default_split}
    form = ExpenseForm(group, request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        expense = form.save_expense(request.user)
        messages.success(request, f'Expense "{expense.title}" was added.')
        return redirect("expense_detail", expense.pk)
    return render(
        request,
        "expenses/expense_form.html",
        {"group": group, "form": form, "mode": "create"},
    )


@login_required
def expense_detail(request, expense_id):
    expense = expense_for_user(request.user, expense_id)
    membership = membership_for(request.user, expense.group)
    shares = expense.shares.select_related("user")
    my_share = next((share for share in shares if share.user_id == request.user.pk), None)
    can_mark_paid = bool(
        my_share
        and request.user.pk != expense.payer_id
        and my_share.status == ExpenseShare.Status.UNPAID
    )
    return render(
        request,
        "expenses/expense_detail.html",
        {
            "expense": expense,
            "group": expense.group,
            "membership": membership,
            "shares": shares,
            "my_share": my_share,
            "can_mark_paid": can_mark_paid,
        },
    )


@login_required
def expense_edit(request, expense_id):
    expense = expense_for_user(request.user, expense_id)
    require_admin(request.user, expense.group)
    form = ExpenseForm(expense.group, request.POST or None, instance=expense)
    if request.method == "POST" and form.is_valid():
        expense = form.save_expense(request.user)
        messages.success(request, "Expense updated.")
        return redirect("expense_detail", expense.pk)
    return render(
        request,
        "expenses/expense_form.html",
        {"group": expense.group, "expense": expense, "form": form, "mode": "edit"},
    )


@login_required
def expense_delete(request, expense_id):
    expense = expense_for_user(request.user, expense_id)
    require_admin(request.user, expense.group)
    if request.method == "POST":
        group_id = expense.group_id
        title = expense.title
        expense.delete()
        messages.success(request, f'Expense "{title}" was deleted.')
        return redirect("expense_list", group_id)
    return render(request, "expenses/expense_confirm_delete.html", {"expense": expense})


@login_required
def expense_split_correct(request, expense_id):
    expense = expense_for_user(request.user, expense_id)
    require_admin(request.user, expense.group)
    form = SplitCorrectionForm(expense, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Expense split corrected.")
        return redirect("expense_detail", expense.pk)
    return render(
        request,
        "expenses/split_form.html",
        {"expense": expense, "group": expense.group, "form": form},
    )


@login_required
def expense_mark_paid(request, expense_id):
    expense = expense_for_user(request.user, expense_id)
    if request.method != "POST":
        return redirect("expense_detail", expense.pk)
    share = expense.shares.filter(user=request.user).first()
    if share is None or request.user.pk == expense.payer_id or share.status == ExpenseShare.Status.PAID:
        return HttpResponseBadRequest("Mark as Paid is unavailable for this share.")
    share.mark_paid()
    messages.success(request, "Your share is marked as Paid.")
    return redirect("expense_detail", expense.pk)


@login_required
def my_payments(request):
    shares = (
        ExpenseShare.objects.filter(user=request.user)
        .select_related("expense", "expense__group", "expense__payer")
        .order_by("status", "expense__due_date")
    )
    return render(request, "expenses/my_payments.html", {"shares": shares})
