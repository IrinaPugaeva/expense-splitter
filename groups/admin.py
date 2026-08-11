from django.contrib import admin

from .models import ExpenseGroup, GroupInvitation, GroupMembership


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_by", "created_at")
    search_fields = ("title", "description", "created_by__email")


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "joined_at")
    list_filter = ("role",)


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ("group", "invited_user", "status", "expires_at")
    list_filter = ("status",)
