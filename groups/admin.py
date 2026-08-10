from django.contrib import admin

from .models import ExpenseGroup, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0


@admin.register(ExpenseGroup)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "default_split", "created_by", "created_at")
    search_fields = ("title", "description", "created_by__email")
    list_filter = ("category", "default_split")
    inlines = (GroupMembershipInline,)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "joined_at")
    list_filter = ("role",)
    search_fields = ("group__title", "user__email")
