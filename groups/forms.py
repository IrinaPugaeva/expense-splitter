from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import ExpenseGroup, GroupInvitation, GroupMembership


FIELD_CLASS = "form-control"


class GroupForm(forms.ModelForm):
    class Meta:
        model = ExpenseGroup
        fields = ("title", "category", "default_split", "description")
        error_messages = {
            "title": {
                "required": "Group title is required.",
                "max_length": "Group title must be 100 characters or fewer.",
            },
            "description": {"required": "Group description is required."},
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": FIELD_CLASS, "placeholder": "Flatmates", "maxlength": 100}
            ),
            "category": forms.Select(attrs={"class": FIELD_CLASS}),
            "default_split": forms.Select(attrs={"class": FIELD_CLASS}),
            "description": forms.Textarea(
                attrs={
                    "class": FIELD_CLASS,
                    "placeholder": "Shared household expenses",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["description"].required = True

    def clean_title(self) -> str:
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Group title is required.")
        duplicate = ExpenseGroup.objects.filter(created_by=self.user, title__iexact=title)
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("A group with this title already exists.")
        return title

    def clean_description(self) -> str:
        description = self.cleaned_data.get("description", "").strip()
        if not description:
            raise forms.ValidationError("Group description is required.")
        return description


class InvitationForm(forms.Form):
    email = forms.EmailField(
        label="Registered account email",
        widget=forms.EmailInput(
            attrs={"class": FIELD_CLASS, "placeholder": "jobaida@test.com"}
        ),
    )

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.invited_user = None

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        user = get_user_model().objects.filter(email__iexact=email).first()
        if user is None:
            raise forms.ValidationError("User not found.")
        if GroupMembership.objects.filter(group=self.group, user=user).exists():
            raise forms.ValidationError("Already a member.")
        if GroupInvitation.objects.filter(
            group=self.group,
            invited_user=user,
            status=GroupInvitation.Status.PENDING,
            expires_at__gt=timezone.now(),
        ).exists():
            raise forms.ValidationError("Already invited.")
        self.invited_user = user
        return email
