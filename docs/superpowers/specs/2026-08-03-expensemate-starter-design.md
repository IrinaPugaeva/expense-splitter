# ExpenseMate Starter Design

## Goal

Build a minimal, presentation-ready Django repository for ExpenseMate that implements two user stories: US002 (login) and US004 (create group), including validation errors, automated tests, setup instructions, and screenshots.

## Source alignment

The implementation follows the uploaded ExpenseMate SRS and UI prototype. It uses the planned technology stack: Python, Django templates, SQLite, HTML/CSS, and Bootstrap-style responsive layouts. The visual structure follows the blue header, left navigation, cards, sign-in page, My Groups page, and Create Group page shown in the prototype.

The public `wkostusiak/ExpenseSplitter` repository is used only as design inspiration for a small responsive Django application, clear feature-oriented README, simple local demo flow, and screenshot-led documentation. No source code is copied.

## Scope

### Implemented

- Login by unique email and password.
- Generic error message for invalid credentials.
- Redirect unauthenticated users to login.
- View groups belonging to the signed-in user.
- Create a group with title, category, default split, and description.
- Automatically assign the creator as Group Admin and create membership.
- Reject an empty group title.
- Reject a group title longer than 100 characters.
- Demo-data setup command.
- Django tests for login, access control, group creation, validation, and group visibility.
- README with local URL, setup, credentials, test scenarios, screenshots, and test command.

### Not implemented

Registration, password reset, PayID profile, invitations, expense management, payments, notifications, editing, and deletion remain future work.

## Architecture

- `accounts`: custom email-based user model and authentication views/forms.
- `groups`: group and membership models, group-list view, group-create view, and validation.
- `expensemate`: project settings and root URL configuration.
- `templates` and `static`: responsive UI matching the prototype.
- `setup_demo` management command: applies migrations and creates a repeatable demo account and example groups.

## Data model

### User

Custom Django user derived from `AbstractUser`:

- `email`: unique and used as `USERNAME_FIELD`.
- `username`: removed.
- `first_name`, `last_name`, password fields: inherited.

### ExpenseGroup

- `title`: required, maximum 100 characters.
- `category`: Household, Travel, Food, Shopping, Other.
- `default_split`: Equal or Custom.
- `description`: optional.
- `created_by`: user who created the group.
- `created_at`, `updated_at`: timestamps.

### GroupMembership

- `group` and `user` foreign keys.
- `role`: Admin or Member.
- Unique constraint on `(group, user)`.

## Error handling

- Invalid login always shows `Invalid email or password. Please try again.` without identifying which field was incorrect.
- Empty titles show `Group title is required.`
- Titles over 100 characters show `Group title must be 100 characters or fewer.`
- Group creation uses an atomic transaction so the group and admin membership are created together.

## Testing

Django `TestCase` coverage includes:

- successful email login;
- unsuccessful login with generic error;
- authentication-required redirects;
- successful group creation and admin membership;
- empty and overlong title rejection;
- users only see groups where they have membership.

A dependency-free static verification script checks repository structure, required README content, screenshot presence, and Python syntax in this execution environment.
