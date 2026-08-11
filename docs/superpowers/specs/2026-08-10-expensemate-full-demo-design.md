# ExpenseMate Full Demonstration Design

## Goal

Extend the approved Django starter into a complete local demonstration build that covers all ExpenseMate user stories and the functional/negative test scenarios in Assessment 3 while keeping the code small, readable, and easy to present.

## Scope

The build implements:

- account registration, email login, local password reset, and logout;
- profile and PayID management;
- group creation, viewing, editing, and conditional deletion;
- invitations, acceptance/decline, member removal, and leaving a group;
- expense creation, payer and participant selection, equal/custom splits, editing, deletion, and split correction;
- group/expense detail views and combined search/filtering;
- PayID display/copy, marking a share paid, and due/overdue reminders;
- Admin versus Member permissions;
- seeded demonstration accounts and data;
- compact test-data guidance on every screen;
- a README demonstration checklist and a separate detailed manual-test document.

Direct banking integration, cloud deployment, native mobile apps, load testing, penetration testing, and external APIs remain out of scope.

## Architecture

Use three Django apps with server-rendered templates:

- `accounts`: custom email user, registration, login, password reset, PayID profile;
- `groups`: groups, memberships, invitations, role checks, group/member operations;
- `expenses`: expenses, shares, split calculations, search, payment state.

Business rules stay in short service/helper functions rather than large views. Views remain function-based where doing so is clearer than generic class-based views. SQLite remains the local database because the user prioritised the simplest possible Mac demo.

## Data Model

### User

- email is the login identifier;
- display name is stored in `first_name`;
- optional `payid`.

### ExpenseGroup

- title, category, default split, description;
- creator and timestamps;
- duplicate titles are prohibited per creator, case-insensitively at form level.

### GroupMembership

- one row per user/group;
- role is `admin` or `member`.

### GroupInvitation

- group, invited user, inviter, status, expiry, timestamps;
- only one pending invitation per user/group.

### Expense

- group, title, amount, date, category, description, due date;
- payer, split method, creator, timestamps.

### ExpenseShare

- expense, participant, share amount, paid status, paid timestamp;
- payer share starts as paid; other shares start unpaid.

## Core Rules

- Every protected view checks group membership.
- Admin-only operations return HTTP 403 when accessed directly by a Member.
- Groups cannot be deleted while any unpaid share exists.
- Members cannot leave or be removed while they have unpaid shares.
- Equal split distributes cents deterministically so totals always match.
- Custom shares must be non-negative and must equal the expense total exactly.
- Identical expense submissions are rejected.
- A share can only be marked paid by its participant; the payer button is not shown.
- Reminder state is derived from `due_date`: paid, overdue, due tomorrow, or unpaid.

## Password Reset Simplification

The local demo does not send email. A known email advances directly to a new-password form, which acts as the reset link for demonstration purposes. Unknown emails display `No account found.` This is documented clearly in the UI and README.

## UI

Keep the current blue/purple ExpenseMate visual language and responsive layout. Remove decorative feature pills such as “Responsive web app”, “Role-based groups”, and “Simple local demo”. Keep role information cards and a small future-version note card, but make its content consistent with the completed build (direct payment integration/cloud notifications).

Every screen includes a compact `Demo test data` panel. Data is centralised in a context processor keyed by URL name, so templates stay readable. The panel contains relevant case IDs, credentials, and example values. Detailed test cases are stored separately in `docs/MANUAL_TEST_CASES.md`.

## Demonstration Data

Seed four accounts:

- Irina: Admin and payer;
- Nicolas: Member with both paid and unpaid examples;
- Jobaida: removable Member with no unpaid obligations in one group;
- Samesh: Member used in participant-selection examples.

Seed groups, invitations, expenses, equal/custom shares, and statuses required to exercise the positive and negative scenarios without manual database edits.

## Testing

Use Django `TestCase` to cover model calculations, validation, permissions, CRUD, invitations, membership rules, search, payment state, and negative scenarios. Manual responsive/cross-browser cases remain documented rather than automated.
