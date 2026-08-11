#!/usr/bin/env python3
"""Dependency-free checks that can run even before Django is installed."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "manage.py",
    "requirements.txt",
    "README.md",
    "start_demo.sh",
    "accounts/models.py",
    "accounts/forms.py",
    "accounts/views.py",
    "accounts/tests.py",
    "groups/models.py",
    "groups/forms.py",
    "groups/services.py",
    "groups/views.py",
    "groups/tests.py",
    "groups/management/commands/setup_demo.py",
    "expenses/models.py",
    "expenses/forms.py",
    "expenses/services.py",
    "expenses/views.py",
    "expenses/tests.py",
    "expensemate/demo_data.py",
    "templates/accounts/login.html",
    "templates/accounts/register.html",
    "templates/groups/group_list.html",
    "templates/groups/group_detail.html",
    "templates/groups/members.html",
    "templates/expenses/expense_form.html",
    "templates/expenses/expense_detail.html",
    "templates/expenses/my_payments.html",
    "templates/includes/demo_test_data.html",
    "static/css/expensemate.css",
    "docs/MANUAL_TEST_CASES.md",
]

SCREENSHOTS = [
    "login.png",
    "invalid-login.png",
    "my-groups.png",
    "create-group.png",
    "group-dashboard.png",
    "add-expense.png",
    "expense-detail.png",
    "my-payments.png",
]

REQUIRED_README_TEXT = [
    "http://127.0.0.1:8000/",
    "irina@test.com",
    "nicolas@test.com",
    "Password1234",
    "bash start_demo.sh",
    "python manage.py setup_demo",
    "python manage.py test",
    "TC-001",
    "TC-031",
    "TC-N001",
    "TC-N031",
    "wkostusiak/ExpenseSplitter",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"invalid PNG signature: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def main() -> None:
    required = REQUIRED_FILES + [f"docs/screenshots/{name}" for name in SCREENSHOTS]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing files: {', '.join(missing)}")

    for path in ROOT.rglob("*.py"):
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            fail(f"Python syntax error in {path.relative_to(ROOT)}: {exc}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    absent = [value for value in REQUIRED_README_TEXT if value not in readme]
    if absent:
        fail(f"README is missing required text: {', '.join(absent)}")

    manual = (ROOT / "docs" / "MANUAL_TEST_CASES.md").read_text(encoding="utf-8")
    expected_ids = [f"TC-{number:03d}" for number in range(1, 32)] + [
        f"TC-N{number:03d}" for number in range(1, 32)
    ]
    absent_ids = [case_id for case_id in expected_ids if case_id not in readme or case_id not in manual]
    if absent_ids:
        fail(f"test IDs missing from README or manual guide: {', '.join(absent_ids)}")

    for template in (ROOT / "templates").rglob("*.html"):
        markup = template.read_text(encoding="utf-8")
        if "<!doctype html>" not in markup.lower() and "{% extends" not in markup and "{% if" not in markup:
            fail(f"template has no document, parent, or partial marker: {template.relative_to(ROOT)}")
        if markup.count("{%") != markup.count("%}"):
            fail(f"unbalanced Django tags: {template.relative_to(ROOT)}")
        if markup.count("{{") != markup.count("}}"):
            fail(f"unbalanced Django variables: {template.relative_to(ROOT)}")

    login_template = (ROOT / "templates" / "accounts" / "login.html").read_text(encoding="utf-8")
    for removed_label in ("Responsive web app", "Role-based groups", "Simple local demo"):
        if removed_label in login_template:
            fail(f"removed promotional label is still present: {removed_label}")

    for name in SCREENSHOTS:
        size = png_size(ROOT / "docs" / "screenshots" / name)
        if size != (1440, 900):
            fail(f"unexpected screenshot size for {name}: {size}")

    css = (ROOT / "static" / "css" / "expensemate.css").read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        fail("CSS braces are unbalanced")

    print("PASS: repository files and all eight screenshots are present")
    print("PASS: Python files compile and template/CSS delimiters are balanced")
    print("PASS: README and manual guide list TC-001–TC-031 and TC-N001–TC-N031")
    print("PASS: removed promotional labels are absent")
    print("PASS: screenshots are valid 1440×900 PNG files")


if __name__ == "__main__":
    main()
