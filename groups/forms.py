from django import forms

from .models import ExpenseGroup


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = ExpenseGroup
        fields = ("title", "category", "default_split", "description")
        error_messages = {
            "title": {
                "required": "Group title is required.",
                "max_length": "Group title must be 100 characters or fewer.",
            }
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Flatmates",
                    "maxlength": 100,
                    "autofocus": True,
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "default_split": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Shared household expenses",
                    "rows": 4,
                }
            ),
        }

    def clean_title(self) -> str:
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Group title is required.")
        if len(title) > 100:
            raise forms.ValidationError("Group title must be 100 characters or fewer.")
        return title
