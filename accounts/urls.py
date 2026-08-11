from django.urls import path

from .views import (
    ExpenseMateLoginView,
    ExpenseMateLogoutView,
    password_reset,
    password_reset_confirm,
    profile,
    register,
)

urlpatterns = [
    path("login/", ExpenseMateLoginView.as_view(), name="login"),
    path("logout/", ExpenseMateLogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
    path("password-reset/", password_reset, name="password_reset"),
    path("password-reset/new/", password_reset_confirm, name="password_reset_confirm"),
    path("profile/", profile, name="profile"),
]
