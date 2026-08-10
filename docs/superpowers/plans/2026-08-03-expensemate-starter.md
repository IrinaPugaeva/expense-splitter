# ExpenseMate Starter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a ZIP-ready Django starter implementing email login and group creation with error handling, tests, README, and screenshots.

**Architecture:** Use a custom email-based Django user model in `accounts`, group and membership models in `groups`, server-rendered templates, SQLite, and a demo setup command. Keep the feature set intentionally small and align the interface with the uploaded role-based MVP prototype.

**Tech Stack:** Python 3.10+, Django 5.2 LTS, SQLite, HTML5, CSS3, responsive Bootstrap-compatible markup, Django TestCase.

## Global Constraints

- Implement only US002 Login and US004 Create Group plus the minimum My Groups page required for navigation.
- Group title is required and limited to 100 characters.
- Group creator becomes Group Admin automatically.
- Use a generic invalid-credentials message.
- Local demo URL is `http://127.0.0.1:8000/`.
- No payment gateway, cloud deployment, native mobile application, or expense splitting logic.

---

### Task 1: Repository scaffolding and test contracts

**Files:**
- Create: `manage.py`, `expensemate/*`, `accounts/tests.py`, `groups/tests.py`, `requirements.txt`

**Interfaces:**
- Produces Django settings with `AUTH_USER_MODEL = "accounts.User"` and named URLs `login`, `logout`, `group_list`, and `group_create`.

- [ ] Write login and group behavior tests before implementation.
- [ ] Run tests and confirm they fail because the application code is not implemented.
- [ ] Add Django project/app scaffolding and dependency pin.

### Task 2: Email authentication

**Files:**
- Create: `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`, migration, templates.

**Interfaces:**
- Produces `User`, `EmailAuthenticationForm`, and login/logout endpoints.

- [ ] Implement custom unique-email user model.
- [ ] Implement generic invalid-login handling.
- [ ] Connect login and logout routes.
- [ ] Verify authentication tests.

### Task 3: Group creation and membership

**Files:**
- Create: `groups/models.py`, `groups/forms.py`, `groups/views.py`, `groups/urls.py`, migration, admin configuration.

**Interfaces:**
- Produces `ExpenseGroup`, `GroupMembership`, `GroupCreateForm`, group list, and create endpoints.

- [ ] Implement models and constraints.
- [ ] Implement form validation messages.
- [ ] Implement atomic creation of group plus admin membership.
- [ ] Filter group list by membership.
- [ ] Verify group tests.

### Task 4: Demo UI and setup

**Files:**
- Create: templates, CSS, `groups/management/commands/setup_demo.py`, startup scripts.

**Interfaces:**
- Produces repeatable demo credentials and responsive pages.

- [ ] Implement UI matching prototype structure.
- [ ] Implement idempotent demo setup command.
- [ ] Add macOS/Linux and Windows startup scripts.
- [ ] Generate screenshots.

### Task 5: Documentation and packaging

**Files:**
- Create: `README.md`, screenshots, `.gitignore`, `LICENSE`, verification script.

**Interfaces:**
- Produces a self-contained ZIP repository.

- [ ] Document project, implemented scope, local link, setup, credentials, errors, testing, and future scope.
- [ ] Run syntax/static verification.
- [ ] Review repository tree and remove generated caches/databases.
- [ ] Create final ZIP.
