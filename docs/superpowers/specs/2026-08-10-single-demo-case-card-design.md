# Single Demo Case Card Design

## Goal

Replace the floating multi-case test panel with one compact, page-specific demo-data card that visually matches the original login-page example.

## Approved UX

- Every route displays at most one demo card.
- The card contains only the data needed to run one main manual test on that page.
- The card does not show a list of negative scenarios or full test instructions.
- The card is part of the normal page flow, never a fixed overlay.
- Full steps for all positive and negative tests remain in `docs/MANUAL_TEST_CASES.md`.
- The login card uses the heading `Demo account` and shows the email and password in the same clean light-grey style as the preferred screenshot.
- Other screens use short headings such as `Demo group`, `Demo expense`, or `Demo PayID`.
- Test-case IDs remain in the data model and accessible markup for traceability, but are not visually prominent.

## Data Model

`expensemate/demo_data.py` maps each Django URL name to one dictionary:

```python
{
    "id": "TC-002",
    "heading": "Demo account",
    "lines": ["irina@test.com", "Password1234"],
}
```

The context processor exposes this as `demo_case` rather than `demo_cases`.

## Template and Layout

`templates/includes/demo_test_data.html` renders one `<aside>` only when `demo_case` exists. It uses a heading and plain lines, with the test-case ID stored in a `data-test-case` attribute and accessible label.

The card is rendered below the page content. Desktop width is capped to keep it visually compact; mobile width is 100%. It uses the existing muted page palette and purple code text.

## Scope

This change affects presentation only. Existing application features, forms, validation, permissions, database models, and manual test documentation remain unchanged.
