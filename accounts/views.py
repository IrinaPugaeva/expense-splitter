from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    EmailAuthenticationForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    ProfileForm,
    RegistrationForm,
)


class ExpenseMateLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class ExpenseMateLogoutView(LogoutView):
    next_page = reverse_lazy("login")


def register(request):
    if request.user.is_authenticated:
        return redirect("group_list")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("group_list")
    return render(request, "accounts/register.html", {"form": form})


def password_reset(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        request.session["password_reset_user_id"] = form.user.pk
        return redirect("password_reset_confirm")
    return render(request, "accounts/password_reset.html", {"form": form})


def password_reset_confirm(request):
    user_id = request.session.get("password_reset_user_id")
    user = get_user_model().objects.filter(pk=user_id).first()
    if user is None:
        return redirect("password_reset")

    form = PasswordResetConfirmForm(user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["password1"])
        user.save(update_fields=["password"])
        request.session.pop("password_reset_user_id", None)
        messages.success(request, "Password updated. You can sign in now.")
        return redirect("login")
    return render(request, "accounts/password_reset_confirm.html", {"form": form, "account": user})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile saved.")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form": form})
