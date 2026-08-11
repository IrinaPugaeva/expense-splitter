from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("groups", "0002_groupinvitation_alter_expensegroup_description"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=100)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("date", models.DateField()),
                ("category", models.CharField(choices=[("food", "Food"), ("utilities", "Utilities"), ("rent", "Rent"), ("travel", "Travel"), ("shopping", "Shopping"), ("other", "Other")], max_length=20)),
                ("description", models.TextField()),
                ("due_date", models.DateField()),
                ("split_method", models.CharField(choices=[("equal", "Equal"), ("custom", "Custom")], default="equal", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_expenses", to=settings.AUTH_USER_MODEL)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expenses", to="groups.expensegroup")),
                ("payer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="paid_expenses", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-date", "-created_at")},
        ),
        migrations.CreateModel(
            name="ExpenseShare",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid", max_length=10)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("expense", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="shares", to="expenses.expense")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="expense_shares", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("user_id",)},
        ),
        migrations.AddConstraint(
            model_name="expenseshare",
            constraint=models.UniqueConstraint(fields=("expense", "user"), name="unique_expense_participant_share"),
        ),
    ]
