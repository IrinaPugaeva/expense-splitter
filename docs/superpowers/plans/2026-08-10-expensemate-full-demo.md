# ExpenseMate Full Demonstration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, readable local ExpenseMate demonstration covering all user stories and test scenarios in Assessment 3.

**Architecture:** Extend the current Django project into three focused apps: accounts, groups, and expenses. Use server-rendered forms/templates, SQLite, small permission/service helpers, and centrally supplied screen-specific demo data.

**Tech Stack:** Python 3.10+, Django 5.2 LTS, SQLite, Django templates, HTML/CSS, small vanilla JavaScript.

## Global Constraints

- Prioritise code simplicity and readability over abstraction.
- Keep local Mac setup to one command: `bash start_demo.sh`.
- Use email as the login identifier.
- Implement all US001–US025 behaviours represented by the supplied test cases.
- Display compact test data on every application screen.
- Keep detailed test cases in a separate document and list demo tests in README.
- Do not add payment gateways, cloud deployment, native mobile code, external APIs, load tests, or penetration tests.

---

### Task 1: Account management

**Files:** `accounts/models.py`, `accounts/forms.py`, `accounts/views.py`, `accounts/urls.py`, `accounts/tests.py`, account templates, migration.

- [ ] Write failing tests for registration, invalid registration, login outcomes, password reset, and PayID update.
- [ ] Implement the minimum model/form/view behaviour.
- [ ] Verify account tests and commit.

### Task 2: Group and membership management

**Files:** `groups/models.py`, `groups/forms.py`, `groups/services.py`, `groups/views.py`, `groups/urls.py`, `groups/tests.py`, group templates, migration.

- [ ] Write failing tests for group CRUD, duplicate/required fields, invitations, accept/decline/expiry, removal/leave rules, and permissions.
- [ ] Implement the minimum model/form/service/view behaviour.
- [ ] Verify group tests and commit.

### Task 3: Expense and payment flow

**Files:** new `expenses/` app, templates, migration, tests.

- [ ] Write failing tests for expense CRUD, payer/participants, equal/custom splits, duplicates, split correction, search, payment state, reminders, and permissions.
- [ ] Implement calculation and persistence services.
- [ ] Implement views/forms/templates.
- [ ] Verify expense tests and commit.

### Task 4: Demo guidance and UI cleanup

**Files:** `expensemate/demo_data.py`, context processor, `templates/base.html`, shared partial, all templates, CSS.

- [ ] Remove feature pills.
- [ ] Add relevant compact test data to every route.
- [ ] Keep role/future-version cards with accurate wording.
- [ ] Verify responsive static structure and commit.

### Task 5: Seed data, documentation, screenshots, packaging

**Files:** demo command, README, `docs/MANUAL_TEST_CASES.md`, screenshots, start scripts, verification tool.

- [ ] Seed all accounts/groups/invitations/expenses required for demonstrations.
- [ ] Add all demonstrable test IDs to README and detailed steps to the separate test document.
- [ ] Update Mac-first run instructions.
- [ ] Generate representative screenshots.
- [ ] Run syntax, repository, Django checks/tests where dependencies are available.
- [ ] Package the clean repository ZIP and record its checksum.
