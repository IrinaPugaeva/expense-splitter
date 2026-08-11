from django.urls import path

from . import views

urlpatterns = [
    path("payments/", views.my_payments, name="my_payments"),
    path("groups/<int:group_id>/expenses/", views.expense_list, name="expense_list"),
    path("groups/<int:group_id>/expenses/add/", views.expense_create, name="expense_create"),
    path("expenses/<int:expense_id>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:expense_id>/edit/", views.expense_edit, name="expense_edit"),
    path("expenses/<int:expense_id>/delete/", views.expense_delete, name="expense_delete"),
    path(
        "expenses/<int:expense_id>/correct-split/",
        views.expense_split_correct,
        name="expense_split_correct",
    ),
    path("expenses/<int:expense_id>/mark-paid/", views.expense_mark_paid, name="expense_mark_paid"),
]
