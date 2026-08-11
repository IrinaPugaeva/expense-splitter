from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command
from django.utils import timezone

from expenses.models import Expense, ExpenseShare
from groups.models import ExpenseGroup, GroupInvitation, GroupMembership


class Command(BaseCommand):
    help = "Apply migrations and recreate repeatable ExpenseMate demonstration data."

    DEMO_PASSWORD = "Password1234"
    DEMO_EMAILS = [
        "irina@test.com",
        "nicolas@test.com",
        "jobaida@test.com",
        "samesh@test.com",
        # Remove accounts from the earlier starter if they exist.
        "irina@torrens.edu.au",
        "nicolas@torrens.edu.au",
        "jobaida@torrens.edu.au",
        "samesh@torrens.edu.au",
    ]

    def handle(self, *args, **options):
        self.stdout.write("Applying database migrations...")
        call_command("migrate", interactive=False, verbosity=0)

        user_model = get_user_model()
        ExpenseGroup.objects.filter(created_by__email__in=self.DEMO_EMAILS).delete()
        user_model.objects.filter(email__in=self.DEMO_EMAILS).delete()

        people = [
            ("irina@test.com", "Irina", "Pugaeva", "irina@payid.bank"),
            ("nicolas@test.com", "Nicolas", "Cortes", "nicolas@payid.bank"),
            ("jobaida@test.com", "Jobaida", "Orni", "jobaida@payid.bank"),
            ("samesh@test.com", "Samesh", "Bajracharya", "samesh@payid.bank"),
        ]
        users = {}
        for email, first_name, last_name, payid in people:
            user = user_model.objects.create_user(
                email=email,
                password=self.DEMO_PASSWORD,
                first_name=first_name,
                last_name=last_name,
                payid=payid,
            )
            users[email] = user

        irina = users["irina@test.com"]
        nicolas = users["nicolas@test.com"]
        jobaida = users["jobaida@test.com"]
        samesh = users["samesh@test.com"]

        flatmates = self.create_group(
            "Flatmates", "Shared household costs", irina, ExpenseGroup.Category.HOUSEHOLD
        )
        grocery = self.create_group(
            "Grocery", "Weekly food and household shopping", irina, ExpenseGroup.Category.FOOD
        )
        summer_trip = self.create_group(
            "Summer trip", "Shared travel expenses", irina, ExpenseGroup.Category.TRAVEL
        )
        online_shopping = self.create_group(
            "Online shopping", "Shared online order", jobaida, ExpenseGroup.Category.SHOPPING
        )
        old_trip = self.create_group(
            "Old trip", "Invitation-expiry example", samesh, ExpenseGroup.Category.TRAVEL
        )

        self.add_members(flatmates, [(irina, "admin"), (nicolas, "member"), (jobaida, "member"), (samesh, "member")])
        self.add_members(grocery, [(irina, "admin"), (jobaida, "member"), (samesh, "member")])
        self.add_members(summer_trip, [(irina, "admin"), (nicolas, "member"), (jobaida, "member")])
        self.add_members(online_shopping, [(jobaida, "admin")])
        self.add_members(old_trip, [(samesh, "admin")])

        GroupInvitation.objects.create(
            group=online_shopping,
            invited_user=nicolas,
            invited_by=jobaida,
            expires_at=timezone.now() + timedelta(days=7),
        )
        GroupInvitation.objects.create(
            group=old_trip,
            invited_user=nicolas,
            invited_by=samesh,
            expires_at=timezone.now() - timedelta(days=1),
        )

        today = timezone.localdate()
        self.create_expense(
            flatmates,
            "Dinner",
            "60.00",
            today,
            Expense.Category.FOOD,
            "Dinner after class",
            today + timedelta(days=3),
            irina,
            Expense.SplitMethod.EQUAL,
            [(irina, "20.00", True), (nicolas, "20.00", False), (jobaida, "20.00", True)],
        )
        self.create_expense(
            flatmates,
            "Electricity bill",
            "160.40",
            today - timedelta(days=20),
            Expense.Category.UTILITIES,
            "Monthly electricity bill",
            today - timedelta(days=5),
            samesh,
            Expense.SplitMethod.EQUAL,
            [(irina, "40.10", True), (nicolas, "40.10", False), (jobaida, "40.10", True), (samesh, "40.10", True)],
        )
        self.create_expense(
            flatmates,
            "Internet",
            "79.00",
            today - timedelta(days=15),
            Expense.Category.UTILITIES,
            "Monthly internet plan",
            today - timedelta(days=7),
            jobaida,
            Expense.SplitMethod.EQUAL,
            [(irina, "19.75", True), (nicolas, "19.75", True), (jobaida, "19.75", True), (samesh, "19.75", True)],
        )
        self.create_expense(
            flatmates,
            "Water bill",
            "80.00",
            today,
            Expense.Category.UTILITIES,
            "Quarterly water bill",
            today + timedelta(days=1),
            irina,
            Expense.SplitMethod.EQUAL,
            [(irina, "40.00", True), (nicolas, "40.00", False)],
        )
        self.create_expense(
            flatmates,
            "Furniture",
            "100.00",
            today - timedelta(days=2),
            Expense.Category.SHOPPING,
            "Shared table",
            today + timedelta(days=5),
            irina,
            Expense.SplitMethod.CUSTOM,
            [(irina, "70.00", True), (nicolas, "30.00", False)],
        )
        self.create_expense(
            flatmates,
            "Cleaning supplies",
            "30.00",
            today - timedelta(days=1),
            Expense.Category.SHOPPING,
            "Kitchen and bathroom supplies",
            today + timedelta(days=4),
            jobaida,
            Expense.SplitMethod.EQUAL,
            [(irina, "10.00", True), (jobaida, "10.00", True), (samesh, "10.00", False)],
        )
        self.create_expense(
            summer_trip,
            "Hotel",
            "300.00",
            today - timedelta(days=30),
            Expense.Category.TRAVEL,
            "Three-night accommodation",
            today - timedelta(days=20),
            irina,
            Expense.SplitMethod.EQUAL,
            [(irina, "100.00", True), (nicolas, "100.00", True), (jobaida, "100.00", True)],
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("URL: http://127.0.0.1:8000/")
        self.stdout.write("Admin demo: irina@test.com / Password1234")
        self.stdout.write("Member demo: nicolas@test.com / Password1234")

    @staticmethod
    def create_group(title, description, creator, category):
        return ExpenseGroup.objects.create(
            title=title,
            description=description,
            category=category,
            default_split=ExpenseGroup.SplitMethod.EQUAL,
            created_by=creator,
        )

    @staticmethod
    def add_members(group, members):
        for user, role in members:
            GroupMembership.objects.create(group=group, user=user, role=role)

    @staticmethod
    def create_expense(
        group,
        title,
        amount,
        date,
        category,
        description,
        due_date,
        payer,
        split_method,
        shares,
    ):
        expense = Expense.objects.create(
            group=group,
            title=title,
            amount=Decimal(amount),
            date=date,
            category=category,
            description=description,
            due_date=due_date,
            payer=payer,
            split_method=split_method,
            created_by=payer,
        )
        now = timezone.now()
        ExpenseShare.objects.bulk_create(
            [
                ExpenseShare(
                    expense=expense,
                    user=user,
                    amount=Decimal(share_amount),
                    status=ExpenseShare.Status.PAID if paid else ExpenseShare.Status.UNPAID,
                    paid_at=now if paid else None,
                )
                for user, share_amount, paid in shares
            ]
        )
        return expense
