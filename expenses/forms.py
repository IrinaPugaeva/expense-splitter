from decimal import Decimal

from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from groups.models import GroupMembership
from .models import Expense
from .services import as_money, replace_expense_shares


FIELD_CLASS = "form-control"


class ExpenseForm(forms.ModelForm):
    payer = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        empty_label="Select payer",
        error_messages={"required": "Select a payer."},
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )
    participants = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        error_messages={"required": "Select at least one participant."},
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Expense
        fields = (
            "title",
            "amount",
            "date",
            "category",
            "description",
            "due_date",
            "payer",
            "participants",
            "split_method",
        )
        error_messages = {
            "title": {"required": "Expense title is required."},
            "amount": {"required": "This field is required."},
            "date": {"required": "This field is required."},
            "category": {"required": "This field is required."},
            "description": {"required": "This field is required."},
            "due_date": {"required": "This field is required."},
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Dinner"}),
            "amount": forms.NumberInput(
                attrs={"class": FIELD_CLASS, "step": "0.01", "placeholder": "120.00"}
            ),
            "date": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
            "category": forms.Select(attrs={"class": FIELD_CLASS}),
            "description": forms.Textarea(
                attrs={"class": FIELD_CLASS, "rows": 3, "placeholder": "Dinner after class"}
            ),
            "due_date": forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
            "split_method": forms.Select(attrs={"class": FIELD_CLASS, "data-split-select": "1"}),
        }

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        users = [membership.user for membership in group.memberships.select_related("user")]
        user_ids = [user.pk for user in users]
        queryset = get_user_model().objects.filter(pk__in=user_ids).order_by("first_name", "email")
        self.fields["payer"].queryset = queryset
        self.fields["participants"].queryset = queryset
        self.fields["description"].required = True

        initial_shares = {}
        if self.instance.pk:
            participant_ids = list(self.instance.shares.values_list("user_id", flat=True))
            self.initial.setdefault("participants", participant_ids)
            initial_shares = dict(self.instance.shares.values_list("user_id", "amount"))

        for user in queryset:
            self.fields[f"share_{user.pk}"] = forms.DecimalField(
                label=user.display_name,
                required=False,
                max_digits=10,
                decimal_places=2,
                initial=initial_shares.get(user.pk),
                widget=forms.NumberInput(
                    attrs={"class": FIELD_CLASS, "step": "0.01", "placeholder": "0.00"}
                ),
            )

    @property
    def participant_rows(self):
        return [
            {"user": user, "share_field": self[f"share_{user.pk}"]}
            for user in self.fields["participants"].queryset
        ]

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        expense_date = cleaned_data.get("date")
        due_date = cleaned_data.get("due_date")
        if expense_date and due_date and due_date < expense_date:
            self.add_error("due_date", "Due date cannot be earlier than the expense date.")

        participants = cleaned_data.get("participants")
        split_method = cleaned_data.get("split_method")
        amount = cleaned_data.get("amount")
        self.custom_shares = None
        if participants and split_method == Expense.SplitMethod.CUSTOM:
            custom = {}
            invalid = False
            for user in participants:
                field_name = f"share_{user.pk}"
                share = cleaned_data.get(field_name)
                if share is None:
                    self.add_error(field_name, "Enter a share amount.")
                    invalid = True
                elif share < 0:
                    self.add_error(field_name, "Share amounts cannot be negative.")
                    invalid = True
                else:
                    custom[user.pk] = as_money(share)
            if not invalid and amount is not None:
                total = sum(custom.values(), Decimal("0.00"))
                if total != as_money(amount):
                    self.add_error(None, f"Shares must total AUD {as_money(amount):.2f}.")
                else:
                    self.custom_shares = custom

        duplicate_fields = [
            "title",
            "amount",
            "date",
            "category",
            "description",
            "due_date",
            "payer",
        ]
        if all(cleaned_data.get(field) not in (None, "") for field in duplicate_fields):
            duplicate = Expense.objects.filter(
                group=self.group,
                title__iexact=cleaned_data["title"].strip(),
                amount=cleaned_data["amount"],
                date=cleaned_data["date"],
                category=cleaned_data["category"],
                description=cleaned_data["description"].strip(),
                due_date=cleaned_data["due_date"],
                payer=cleaned_data["payer"],
            )
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                self.add_error(None, "An identical expense already exists.")
        return cleaned_data

    @transaction.atomic
    def save_expense(self, created_by):
        expense = self.save(commit=False)
        expense.group = self.group
        if not expense.pk:
            expense.created_by = created_by
        expense.save()
        participants = list(self.cleaned_data["participants"])
        custom = self.custom_shares if expense.split_method == Expense.SplitMethod.CUSTOM else None
        replace_expense_shares(expense, participants, custom)
        return expense


class SplitCorrectionForm(forms.Form):
    def __init__(self, expense, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expense = expense
        for share in expense.shares.select_related("user"):
            self.fields[f"share_{share.user_id}"] = forms.DecimalField(
                label=share.user.display_name,
                max_digits=10,
                decimal_places=2,
                initial=share.amount,
                widget=forms.NumberInput(attrs={"class": FIELD_CLASS, "step": "0.01"}),
            )

    def clean(self):
        cleaned_data = super().clean()
        values = []
        for field_name in self.fields:
            value = cleaned_data.get(field_name)
            if value is not None and value < 0:
                self.add_error(field_name, "Share amounts cannot be negative.")
            elif value is not None:
                values.append(as_money(value))
        if not self.errors and sum(values, Decimal("0.00")) != as_money(self.expense.amount):
            self.add_error(None, f"Shares must total AUD {self.expense.amount:.2f}.")
        return cleaned_data

    @transaction.atomic
    def save(self):
        for share in self.expense.shares.all():
            share.amount = as_money(self.cleaned_data[f"share_{share.user_id}"])
            share.save(update_fields=["amount"])


class ExpenseSearchForm(forms.Form):
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": FIELD_CLASS, "placeholder": "Search title"}),
    )
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories"), *Expense.Category.choices],
        widget=forms.Select(attrs={"class": FIELD_CLASS}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": FIELD_CLASS, "type": "date"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("date_from")
        end = cleaned_data.get("date_to")
        if start and end and end < start:
            self.add_error("date_to", "End date cannot be earlier than start date.")
        return cleaned_data
