from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password


FIELD_CLASS = "form-control"


class RegistrationForm(UserCreationForm):
    name = forms.CharField(
        label="Name",
        error_messages={"required": "Name is required."},
        widget=forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Irina"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": FIELD_CLASS, "placeholder": "irina@test.com", "autocomplete": "email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Password1234", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": FIELD_CLASS, "placeholder": "Repeat password", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ("name", "email", "password1", "password2")

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Account with this email already exists.")
        return email

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if password2:
            validate_password(password2, self.instance)
        return password2

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["name"].strip()
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(forms.Form):
    """Small login form with the exact demo error messages from the test plan."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": FIELD_CLASS,
                "placeholder": "student@torrens.edu.au",
                "autocomplete": "email",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": FIELD_CLASS,
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not email or not password:
            return cleaned_data

        self.user_cache = get_user_model().objects.filter(email__iexact=email).first()
        if self.user_cache is None:
            raise forms.ValidationError("No account found.")
        if not self.user_cache.check_password(password):
            self.user_cache = None
            raise forms.ValidationError("Invalid credentials.")
        if not self.user_cache.is_active:
            self.user_cache = None
            raise forms.ValidationError("This account is inactive.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": FIELD_CLASS, "placeholder": "irina@test.com"}),
    )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        user = get_user_model().objects.filter(email__iexact=email).first()
        if user is None:
            raise forms.ValidationError("No account found.")
        self.user = user
        return email


class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": FIELD_CLASS, "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": FIELD_CLASS, "autocomplete": "new-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if password2:
            validate_password(password2, self.user)
        return password2


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "payid")
        labels = {"first_name": "Name", "payid": "PayID"}
        widgets = {
            "first_name": forms.TextInput(attrs={"class": FIELD_CLASS}),
            "payid": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "irina@payid.bank"}
            ),
        }
