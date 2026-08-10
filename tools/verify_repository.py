#!/usr/bin/env python3
"""Dependency-free verification for repository packaging."""
from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "manage.py",
    "requirements.txt",
    "README.md",
    "accounts/models.py",
    "accounts/forms.py",
    "accounts/views.py",
    "accounts/tests.py",
    "groups/models.py",
    "groups/forms.py",
    "groups/views.py",
    "groups/tests.py",
    "groups/management/commands/setup_demo.py",
    "templates/accounts/login.html",
    "templates/groups/group_list.html",
    "templates/groups/group_form.html",
    "static/css/expensemate.css",
    "docs/screenshots/login.png",
    "docs/screenshots/invalid-login.png",
    "docs/screenshots/my-groups.png",
    "docs/screenshots/create-group.png",
    "docs/screenshots/invalid-group.png",
]

REQUIRED_README_TEXT = [
    "http://127.0.0.1:8000/",
    "irina@torrens.edu.au",
    "ExpenseMate123!",
    "python manage.py setup_demo",
    "python manage.py test",
    "US002",
    "US004",
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
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing files: {', '.join(missing)}")

    for path in ROOT.rglob("*.py"):
        if ".git" in path.parts or ".venv" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            fail(f"Python syntax error in {path.relative_to(ROOT)}: {exc}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    absent = [value for value in REQUIRED_README_TEXT if value not in readme]
    if absent:
        fail(f"README is missing required text: {', '.join(absent)}")

    for template in (ROOT / "templates").rglob("*.html"):
        markup = template.read_text(encoding="utf-8")
        if "<!doctype html>" not in markup.lower() and "{% extends" not in markup:
            fail(f"template has no document or template parent: {template.relative_to(ROOT)}")
        if markup.count("{%") != markup.count("%}"):
            fail(f"unbalanced Django tags: {template.relative_to(ROOT)}")
        if markup.count("{{") != markup.count("}}"):
            fail(f"unbalanced Django variables: {template.relative_to(ROOT)}")

    for screenshot in (ROOT / "docs" / "screenshots").glob("*.png"):
        size = png_size(screenshot)
        if size != (1440, 900):
            fail(f"unexpected screenshot size for {screenshot.name}: {size}")

    css = (ROOT / "static" / "css" / "expensemate.css").read_text(encoding="utf-8")
    if css.count("{") != css.count("}"):
        fail("CSS braces are unbalanced")

    print("PASS: required repository files are present")
    print("PASS: Python files compile successfully")
    print("PASS: README includes local URL, credentials, setup, tests, and user stories")
    print("PASS: Django template markers and CSS braces are balanced")
    print("PASS: all five screenshots are valid 1440×900 PNG files")


if __name__ == "__main__":
    main()
