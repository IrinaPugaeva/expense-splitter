from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import GroupCreateForm
from .models import ExpenseGroup, GroupMembership


class GroupListView(LoginRequiredMixin, ListView):
    template_name = "groups/group_list.html"
    context_object_name = "memberships"

    def get_queryset(self):
        return (
            GroupMembership.objects.filter(user=self.request.user)
            .select_related("group", "group__created_by")
            .prefetch_related("group__memberships")
            .order_by("-group__created_at")
        )


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = ExpenseGroup
    form_class = GroupCreateForm
    template_name = "groups/group_form.html"
    success_url = reverse_lazy("group_list")

    def form_valid(self, form):
        with transaction.atomic():
            group = form.save(commit=False)
            group.created_by = self.request.user
            group.save()
            GroupMembership.objects.create(
                group=group,
                user=self.request.user,
                role=GroupMembership.Role.ADMIN,
            )
        messages.success(self.request, f'Group "{group.title}" was created successfully.')
        return redirect(self.success_url)
