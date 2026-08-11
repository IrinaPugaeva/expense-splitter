from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GroupForm, InvitationForm
from .models import ExpenseGroup, GroupInvitation, GroupMembership
from .services import (
    group_for_user,
    group_has_unpaid_shares,
    membership_for,
    require_admin,
    user_has_unpaid_shares,
)


def _group_detail_context(user, group, action_error=""):
    membership = membership_for(user, group)
    return {
        "group": group,
        "membership": membership,
        "memberships": group.memberships.select_related("user"),
        "recent_expenses": group.expenses.select_related("payer").prefetch_related("shares")[:5],
        "action_error": action_error,
    }


def _members_context(user, group, form=None, action_error=""):
    membership = membership_for(user, group)
    is_admin = membership.role == GroupMembership.Role.ADMIN
    return {
        "group": group,
        "membership": membership,
        "memberships": group.memberships.select_related("user"),
        "pending_invitations": group.invitations.filter(
            status=GroupInvitation.Status.PENDING
        ).select_related("invited_user"),
        "form": form if form is not None else (InvitationForm(group) if is_admin else None),
        "action_error": action_error,
    }


@login_required
def group_list(request):
    memberships = (
        GroupMembership.objects.filter(user=request.user)
        .select_related("group", "group__created_by")
        .prefetch_related("group__memberships")
        .order_by("-group__created_at")
    )
    invitations = GroupInvitation.objects.filter(
        invited_user=request.user,
        status=GroupInvitation.Status.PENDING,
    ).select_related("group", "invited_by")
    return render(
        request,
        "groups/group_list.html",
        {"memberships": memberships, "invitations": invitations},
    )


@login_required
def group_create(request):
    form = GroupForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            GroupMembership.objects.create(
                group=group, user=request.user, role=GroupMembership.Role.ADMIN
            )
        messages.success(request, f'Group "{group.title}" was created successfully.')
        return redirect("group_detail", group.pk)
    return render(request, "groups/group_form.html", {"form": form, "mode": "create"})


@login_required
def group_detail(request, group_id):
    group = group_for_user(request.user, group_id)
    return render(request, "groups/group_detail.html", _group_detail_context(request.user, group))


@login_required
def group_edit(request, group_id):
    group = group_for_user(request.user, group_id)
    require_admin(request.user, group)
    form = GroupForm(request.user, request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Group information updated.")
        return redirect("group_detail", group.pk)
    return render(
        request,
        "groups/group_form.html",
        {"form": form, "group": group, "mode": "edit"},
    )


@login_required
def group_delete(request, group_id):
    group = group_for_user(request.user, group_id)
    require_admin(request.user, group)
    error = ""
    if request.method == "POST":
        if group_has_unpaid_shares(group):
            error = "All expenses must be settled before the group can be deleted."
        else:
            title = group.title
            group.delete()
            messages.success(request, f'Group "{title}" was deleted.')
            return redirect("group_list")
    return render(request, "groups/group_confirm_delete.html", {"group": group, "action_error": error})


@login_required
def group_members(request, group_id):
    group = group_for_user(request.user, group_id)
    return render(request, "groups/members.html", _members_context(request.user, group))


@login_required
def group_invite(request, group_id):
    group = group_for_user(request.user, group_id)
    require_admin(request.user, group)
    if request.method != "POST":
        return redirect("group_members", group.pk)
    form = InvitationForm(group, request.POST)
    if form.is_valid():
        GroupInvitation.objects.create(
            group=group,
            invited_user=form.invited_user,
            invited_by=request.user,
        )
        messages.success(request, f"Invitation sent to {form.invited_user.email}.")
        return redirect("group_members", group.pk)
    return render(request, "groups/members.html", _members_context(request.user, group, form=form))


@login_required
def invitation_accept(request, invitation_id):
    invitation = get_object_or_404(
        GroupInvitation, pk=invitation_id, invited_user=request.user
    )
    if request.method != "POST":
        return redirect("group_list")
    if invitation.status != GroupInvitation.Status.PENDING or invitation.is_expired:
        return HttpResponseBadRequest("Invitation no longer valid.")
    with transaction.atomic():
        GroupMembership.objects.get_or_create(
            group=invitation.group,
            user=request.user,
            defaults={"role": GroupMembership.Role.MEMBER},
        )
        invitation.status = GroupInvitation.Status.ACCEPTED
        invitation.save(update_fields=["status", "updated_at"])
    messages.success(request, f'You joined "{invitation.group.title}".')
    return redirect("group_detail", invitation.group.pk)


@login_required
def invitation_decline(request, invitation_id):
    invitation = get_object_or_404(
        GroupInvitation, pk=invitation_id, invited_user=request.user
    )
    if request.method == "POST" and invitation.status == GroupInvitation.Status.PENDING:
        invitation.status = GroupInvitation.Status.DECLINED
        invitation.save(update_fields=["status", "updated_at"])
        messages.success(request, "Invitation declined.")
    return redirect("group_list")


@login_required
def group_remove_member(request, group_id, membership_id):
    group = group_for_user(request.user, group_id)
    require_admin(request.user, group)
    target = get_object_or_404(GroupMembership, pk=membership_id, group=group)
    if request.method != "POST":
        return redirect("group_members", group.pk)
    if target.role == GroupMembership.Role.ADMIN:
        error = "The Group Admin cannot be removed."
    elif user_has_unpaid_shares(target.user, group):
        error = "Member has unpaid obligations."
    else:
        name = target.user.display_name
        target.delete()
        messages.success(request, f"{name} was removed from the group.")
        return redirect("group_members", group.pk)
    return render(
        request,
        "groups/members.html",
        _members_context(request.user, group, action_error=error),
    )


@login_required
def group_leave(request, group_id):
    group = group_for_user(request.user, group_id)
    membership = membership_for(request.user, group)
    if request.method != "POST":
        return redirect("group_detail", group.pk)
    if membership.role == GroupMembership.Role.ADMIN:
        error = "The Group Admin cannot leave the group."
    elif user_has_unpaid_shares(request.user, group):
        error = "Pay all shares first before leaving the group."
    else:
        membership.delete()
        messages.success(request, f'You left "{group.title}".')
        return redirect("group_list")
    return render(
        request,
        "groups/group_detail.html",
        _group_detail_context(request.user, group, action_error=error),
    )
