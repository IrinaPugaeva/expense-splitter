# ExpenseMate Manual Test Cases

This document is the separate demonstration checklist requested for the ExpenseMate screens. It follows Section 7 of the Assessment 3 Project Test Plan. The local demo uses SQLite and an on-screen password reset rather than email delivery, but the user-visible outcome is the same.

## Reset the demonstration before a new run

```bash
source .venv/bin/activate
python manage.py setup_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Seeded accounts

| Role | Email | Password | Main use |
|---|---|---|---|
| Group Admin | `irina@test.com` | `Password1234` | Admin CRUD, payer, PayID |
| Group Member | `nicolas@test.com` | `Password1234` | Invitations, unpaid shares, Member permissions |
| Group Member | `jobaida@test.com` | `Password1234` | Paid shares, removable member |
| Group Member | `samesh@test.com` | `Password1234` | Participant exclusion and payer examples |

---

# Functional acceptance cases

## 7.1 Account Management

### TC-001 — US001 Registration

**Precondition:** `irina.new@test.com` is not registered.

1. Open **Create account**.
2. Enter `New Irina`, `irina.new@test.com`, `Password1234`, and the same confirmation.
3. Select **Create account**.

**Expected:** the account is created, the user is signed in, and the empty **My groups** dashboard opens.

### TC-002 — US002 Login

1. Open **Sign in**.
2. Enter `irina@test.com` and `Password1234`.
3. Select **Sign in**.

**Expected:** the dashboard opens and Irina's groups are visible.

### TC-003 — US024 Password reset

1. Select **Forgot password?**.
2. Enter `irina@test.com`.
3. Continue to the local demo reset form.
4. Enter `Password5678` twice and save.
5. Sign in with the new password.

**Expected:** the password is updated and login succeeds. Run `python manage.py setup_demo` afterwards to restore `Password1234`.

## 7.2 Profile Management

### TC-004 — US003 Add or update PayID

1. Sign in as Irina and open **Profile**.
2. Enter `irina@payid.bank`.
3. Select **Save profile**.

**Expected:** the PayID remains visible after refresh and is shown to debtors on expense details.

## 7.3 Group Operations

### TC-005 — US004 Create group

1. Select **Create group**.
2. Enter `Flatmates 2` and `Shared costs`.
3. Select **Create group**.

**Expected:** the group is created, Irina is Admin, and the group dashboard opens.

### TC-006 — US020 Edit group information

1. As Irina, open a group and select **Edit group**.
2. Change the title to `Flatmates updated`.
3. Save.

**Expected:** the new title is displayed. When signed in as Nicolas, the edit control is absent.

### TC-007 — US022 Delete group

1. As Irina, open **Summer trip**; its seeded expense is fully paid.
2. Select **Delete group** and confirm.

**Expected:** the group and its related records are removed. Reset demo data after the test.

## 7.4 Membership Management

### TC-008 — US006 Invite user

1. Register a new account such as `newmember@test.com`.
2. Sign back in as Irina.
3. Open **Flatmates → Members**.
4. Enter the new account email and select **Send invitation**.

**Expected:** a Pending invitation is shown.

### TC-009 — US007 Accept or decline invitation

1. Sign in as Nicolas.
2. On **My groups**, find **Online shopping**.
3. Select **Accept**, reset the demo, then repeat and select **Decline**.

**Expected:** Accept creates a Member record and opens the group; Decline removes the pending invitation from the dashboard.

### TC-010 — US018 Leave group

1. Sign in as Nicolas.
2. Open **Summer trip**.
3. Select **Leave group** and confirm.

**Expected:** Nicolas is removed because all of his Summer trip shares are paid.

### TC-011 — US023 Admin removes member

1. Sign in as Irina and open **Flatmates → Members**.
2. Select **Remove** beside Jobaida.

**Expected:** Jobaida is removed because she has no unpaid Flatmates share.

## 7.5 Expense Management

### TC-012 — US009 Add expense

1. Open **Flatmates → Add expense**.
2. Enter title `Demo lunch`, amount `60.00`, today's date, category Food, description `Lunch after class`, and a future due date.
3. Select Irina as payer, Irina/Nicolas/Jobaida as participants, and Equal split.
4. Save.

**Expected:** all fields are stored and the detail page opens.

### TC-013 — US010 Select payer

Use TC-012 and select Irina in **Paid by**.

**Expected:** the detail page says `Paid by Irina`.

### TC-014 — US011 Select participants

Use amount `60.00`, select Irina/Nicolas/Jobaida, and leave Samesh unselected.

**Expected:** three AUD 20.00 shares are created and Samesh has no share.

### TC-015 — US012 Equal or custom split

1. Create an AUD 100.00 expense for Irina and Nicolas with Equal split.
2. Create another with Custom split and enter `70.00` / `30.00`.

**Expected:** both methods save and total AUD 100.00.

### TC-016 — US019 Edit expense

1. As Irina, open **Dinner**.
2. Select **Edit expense**, change title and amount, and save.

**Expected:** the UI and database display the updated values. Nicolas has no edit control.

### TC-017 — US021 Delete expense

1. As Irina, open an expense.
2. Select **Delete expense** and confirm.

**Expected:** the expense and shares disappear. Reset demo data afterwards.

### TC-018 — US025 Correct split

1. As Irina, open **Furniture**.
2. Select **Correct split**.
3. Change Irina/Nicolas from `70.00 / 30.00` to `60.00 / 40.00`.
4. Save.

**Expected:** the revised shares are displayed and total AUD 100.00.

## 7.6 Viewing and Searching

### TC-019 — US005 View all groups

Sign in as Irina.

**Expected:** **Flatmates**, **Grocery**, and **Summer trip** are listed and each opens the correct dashboard.

### TC-020 — US008 View group details

Open **Flatmates**.

**Expected:** title, description, members with roles, and recent expenses are displayed.

### TC-021 — US013 Search and filter

1. Open **Flatmates → Expenses**.
2. Search title `Dinner`.
3. Filter category Food.
4. Use today's date as both From and To.
5. Combine all filters.

**Expected:** only matching expenses are displayed.

### TC-022 — US014 View expense details

Open **Dinner**.

**Expected:** amount, dates, category, payer, participants, share amounts, and payment statuses are displayed.

## 7.7 Payment Flow

### TC-023 — US015 View and copy PayID

1. Sign in as Nicolas and open **Dinner**.
2. Check `irina@payid.bank`.
3. Select **Copy PayID**.

**Expected:** the PayID is copied and the button changes to `Copied`.

### TC-024 — US016 Mark as paid

1. Sign in as Nicolas and open **Dinner**.
2. Select **Mark as paid** and confirm.

**Expected:** Nicolas's Dinner status becomes Paid.

### TC-025 — US017 Payment reminders

Sign in as Nicolas and open **My payments**.

**Expected:** Water bill is `Payment due tomorrow`, Electricity bill is `Overdue`, and Internet is `Paid`.

---

# Non-functional manual cases

- **TC-026 Chrome:** execute TC-001–TC-025 in the latest Chrome.
- **TC-027 Firefox:** execute TC-001–TC-025 in the latest Firefox.
- **TC-028 Safari:** execute TC-001–TC-025 in the latest Safari.
- **TC-029 Desktop/Laptop:** check 1920×1080 and 1366×768 layouts.
- **TC-030 Tablet:** check a 768×1024 responsive viewport.
- **TC-031 Smartphone:** check a 375×812 responsive viewport and all controls.

---

# Negative test scenarios

### TC-N001 — Invalid registration email
Use `irina@` with otherwise valid registration data. **Expected:** email validation; no account.

### TC-N002 — Weak password
Use `Pass1`. **Expected:** password validation; no account.

### TC-N003 — Wrong password
Use `irina@test.com` / `Password9999`. **Expected:** `Invalid credentials.` and no login.

### TC-N004 — Unknown email
Use `unknown@test.com` / `Password1234`. **Expected:** `No account found.` and no login.

### TC-N005 — Delete group with unpaid expenses
As Irina, attempt to delete **Flatmates**. **Expected:** `All expenses must be settled`; group remains.

### TC-N006 — Password confirmation mismatch
Register with `Password1234` / `Password1235`. **Expected:** `Passwords do not match`; no account.

### TC-N007 — Leave group with unpaid share
As Nicolas, leave **Flatmates**. **Expected:** `Pay all shares first`; membership remains.

### TC-N008 — Remove member with unpaid share
As Irina, remove Nicolas from Flatmates. **Expected:** `Member has unpaid obligations`; membership remains.

### TC-N009 — Incorrect custom total
Create AUD 100.00 with custom `80.00 / 10.00`. **Expected:** shares must total AUD 100.00; no expense.

### TC-N010 — Member attempts to edit expense
As Nicolas, open **Dinner**. **Expected:** Edit is not shown; direct URL returns 403.

### TC-N011 — Member attempts to delete expense
As Nicolas, open **Dinner**. **Expected:** Delete is not shown; direct URL returns 403.

### TC-N012 — Payer attempts to mark own share paid
As Irina, open **Dinner**. **Expected:** Mark as paid is unavailable for the payer.

### TC-N013 — Invite unknown email
As Admin, invite `unknown@test.com`. **Expected:** `User not found`; no invitation.

### TC-N014 — Invite already invited user
In **Online shopping**, invite `nicolas@test.com` again as Jobaida. **Expected:** `Already invited`; one invitation only.

### TC-N015 — Invite existing member
In **Flatmates**, invite `nicolas@test.com`. **Expected:** `Already a member`; no invitation.

### TC-N016 — Accept expired invitation
As Nicolas, accept **Old trip**. **Expected:** `Invitation no longer valid`; no membership.

### TC-N017 — Missing expense title
Leave title blank. **Expected:** `Expense title is required`; no expense.

### TC-N018 — Negative expense amount
Use `-50.00`. **Expected:** `Amount must be greater than 0`; no expense.

### TC-N019 — Negative custom share
Correct a split with `110.00 / -10.00`. **Expected:** negative-share validation; split unchanged.

### TC-N020 — Duplicate account
Register `irina@test.com` again. **Expected:** duplicate-account message; one account.

### TC-N021 — Duplicate expense
Submit the seeded Dinner values again: `Dinner`, `60.00`, today's date, Food, `Dinner after class`, seeded due date, payer Irina. **Expected:** identical-expense warning; no duplicate.

### TC-N022 — Duplicate group
Create `Flatmates` again as Irina. **Expected:** duplicate-group warning; no second group.

### TC-N023 — Missing group fields
Try blank title, then `Flatmates 2` with blank description. **Expected:** required message in each attempt; no group.

### TC-N024 — Missing other required expense fields
Repeat with Amount, Date, Category, Description, or Due date blank. **Expected:** required message; no incomplete expense.

### TC-N025 — No payer selected
Leave Paid by blank. **Expected:** `Select a payer`; no expense.

### TC-N026 — No participants selected
Clear all participants. **Expected:** `Select at least one participant`; no expense.

### TC-N027 — Zero expense amount
Use `0.00`. **Expected:** `Amount must be greater than 0`; no expense.

### TC-N028 — Missing account name
Leave Name blank. **Expected:** `Name is required`; no account.

### TC-N029 — Password reset for unknown email
Use `unknown@test.com`. **Expected:** `No account found`; reset cannot continue.

### TC-N030 — Member attempts to delete group
As Nicolas, open Flatmates. **Expected:** Delete Group is absent; direct URL returns 403.

### TC-N031 — Member manages membership
As Nicolas, open Flatmates Members. **Expected:** Invite and Remove controls are absent; direct POST requests return 403.
