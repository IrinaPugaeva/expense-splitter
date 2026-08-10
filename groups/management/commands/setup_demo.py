from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command

from groups.models import ExpenseGroup, GroupMembership


class Command(BaseCommand):
    help = "Apply migrations and create repeatable ExpenseMate demo data."

    DEMO_PASSWORD = "ExpenseMate123!"

    def handle(self, *args, **options):
        self.stdout.write("Applying database migrations...")
        call_command("migrate", interactive=False, verbosity=0)

        user_model = get_user_model()
        people = [
            ("irina@torrens.edu.au", "Irina", "Pugaeva"),
            ("nicolas@torrens.edu.au", "Nicolas", "Cortes"),
            ("jobaida@torrens.edu.au", "Jobaida", "Orni"),
            ("samesh@torrens.edu.au", "Samesh", "Bajracharya"),
        ]
        users = {}
        for email, first_name, last_name in people:
            user, _ = user_model.objects.get_or_create(
                email=email,
                defaults={"first_name": first_name, "last_name": last_name},
            )
            user.first_name = first_name
            user.last_name = last_name
            user.set_password(self.DEMO_PASSWORD)
            user.save()
            users[email] = user

        grocery, _ = ExpenseGroup.objects.get_or_create(
            title="Grocery",
            created_by=users["irina@torrens.edu.au"],
            defaults={
                "category": ExpenseGroup.Category.HOUSEHOLD,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
                "description": "Weekly food and household shopping",
            },
        )
        summer_trip, _ = ExpenseGroup.objects.get_or_create(
            title="Summer trip",
            created_by=users["irina@torrens.edu.au"],
            defaults={
                "category": ExpenseGroup.Category.TRAVEL,
                "default_split": ExpenseGroup.SplitMethod.EQUAL,
                "description": "Shared travel expenses",
            },
        )

        for user in users.values():
            GroupMembership.objects.update_or_create(
                group=grocery,
                user=user,
                defaults={
                    "role": (
                        GroupMembership.Role.ADMIN
                        if user.email == "irina@torrens.edu.au"
                        else GroupMembership.Role.MEMBER
                    )
                },
            )
        for email in ("irina@torrens.edu.au", "nicolas@torrens.edu.au", "jobaida@torrens.edu.au"):
            GroupMembership.objects.update_or_create(
                group=summer_trip,
                user=users[email],
                defaults={
                    "role": (
                        GroupMembership.Role.ADMIN
                        if email == "irina@torrens.edu.au"
                        else GroupMembership.Role.MEMBER
                    )
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("URL: http://127.0.0.1:8000/")
        self.stdout.write("Email: irina@torrens.edu.au")
        self.stdout.write(f"Password: {self.DEMO_PASSWORD}")
