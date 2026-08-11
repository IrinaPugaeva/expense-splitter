"""One concise, screen-specific data card for the classroom demonstration."""

DEMO_CASES_BY_ROUTE = {
    "login": {
        "id": "TC-002",
        "heading": "Demo account",
        "lines": ["irina@test.com", "Password1234"],
    },
    "register": {
        "id": "TC-001",
        "heading": "Demo registration",
        "lines": [
            "Name: New Irina",
            "Email: irina.new@test.com",
            "Password: Password1234",
        ],
    },
    "password_reset": {
        "id": "TC-003",
        "heading": "Demo password reset",
        "lines": ["Email: irina@test.com", "New password: Password5678"],
    },
    "password_reset_confirm": {
        "id": "TC-003",
        "heading": "Demo new password",
        "lines": ["Password: Password5678", "Confirm: Password5678"],
    },
    "profile": {
        "id": "TC-004",
        "heading": "Demo PayID",
        "lines": ["irina@payid.bank"],
    },
    "group_list": {
        "id": "TC-019",
        "heading": "Demo groups",
        "lines": ["Flatmates", "Grocery", "Summer trip"],
    },
    "group_create": {
        "id": "TC-005",
        "heading": "Demo group",
        "lines": ["Title: Flatmates 2", "Description: Shared costs"],
    },
    "group_edit": {
        "id": "TC-006",
        "heading": "Demo group update",
        "lines": ["New title: Flatmates updated"],
    },
    "group_detail": {
        "id": "TC-020",
        "heading": "Demo group",
        "lines": ["Flatmates", "Check members, roles and expenses"],
    },
    "group_leave": {
        "id": "TC-010",
        "heading": "Demo leave group",
        "lines": ["Group: Summer trip", "All shares are paid"],
    },
    "group_delete": {
        "id": "TC-007",
        "heading": "Demo group deletion",
        "lines": ["Group: Summer trip", "All expenses are settled"],
    },
    "group_members": {
        "id": "TC-008",
        "heading": "Demo invitation",
        "lines": ["Email: newmember@test.com", "Register this account first"],
    },
    "group_invite": {
        "id": "TC-008",
        "heading": "Demo invitation",
        "lines": ["Email: newmember@test.com", "Expected status: Pending"],
    },
    "group_remove_member": {
        "id": "TC-011",
        "heading": "Demo member removal",
        "lines": ["Member: Jobaida", "No unpaid obligations"],
    },
    "invitation_accept": {
        "id": "TC-009",
        "heading": "Demo invitation",
        "lines": ["Login: nicolas@test.com", "Accept: Online shopping"],
    },
    "invitation_decline": {
        "id": "TC-009",
        "heading": "Demo invitation",
        "lines": ["Login: nicolas@test.com", "Decline: Online shopping"],
    },
    "expense_list": {
        "id": "TC-021",
        "heading": "Demo filters",
        "lines": ["Title: Dinner", "Category: Food"],
    },
    "expense_create": {
        "id": "TC-012",
        "heading": "Demo expense",
        "lines": [
            "Title: Demo lunch",
            "Amount: AUD 60.00",
            "Payer: Irina",
            "Participants: Irina, Nicolas, Jobaida",
        ],
    },
    "expense_edit": {
        "id": "TC-016",
        "heading": "Demo expense update",
        "lines": ["New title: Dinner updated", "New amount: AUD 90.00"],
    },
    "expense_delete": {
        "id": "TC-017",
        "heading": "Demo expense deletion",
        "lines": ["Expense: Dinner", "Confirm deletion"],
    },
    "expense_split_correct": {
        "id": "TC-018",
        "heading": "Demo corrected split",
        "lines": ["Expense: Furniture", "Irina: AUD 60.00", "Nicolas: AUD 40.00"],
    },
    "expense_detail": {
        "id": "TC-023",
        "heading": "Demo payment",
        "lines": ["Login: nicolas@test.com", "PayID: irina@payid.bank", "Click Copy PayID"],
    },
    "expense_mark_paid": {
        "id": "TC-024",
        "heading": "Demo payment",
        "lines": ["Login: nicolas@test.com", "Expense: Dinner", "Click Mark as paid"],
    },
    "my_payments": {
        "id": "TC-025",
        "heading": "Demo statuses",
        "lines": ["Water bill: due tomorrow", "Electricity bill: overdue", "Internet: paid"],
    },
}


def demo_test_data(request):
    """Return one small demo-data card for the current named route."""
    route_name = getattr(getattr(request, "resolver_match", None), "url_name", None)
    return {"demo_case": DEMO_CASES_BY_ROUTE.get(route_name)}
