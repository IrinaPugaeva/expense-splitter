from django.contrib import admin

from .models import Expense, ExpenseShare


class ExpenseShareInline(admin.TabularInline):
    model = ExpenseShare
    extra = 0


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "amount", "payer", "date", "due_date")
    list_filter = ("category", "split_method")
    search_fields = ("title", "description", "group__title")
    inlines = (ExpenseShareInline,)


@admin.register(ExpenseShare)
class ExpenseShareAdmin(admin.ModelAdmin):
    list_display = ("expense", "user", "amount", "status", "paid_at")
    list_filter = ("status",)
