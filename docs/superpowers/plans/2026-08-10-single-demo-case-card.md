# Single Demo Case Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show exactly one compact, page-specific demo-data card per ExpenseMate screen.

**Architecture:** Convert the context processor from a list-based `demo_cases` API to one `demo_case` dictionary per route. Render the card in normal document flow using one reusable include and update generated screenshots to match.

**Tech Stack:** Python 3, Django templates, CSS, Pillow screenshot generator, `unittest` static regression checks.

## Global Constraints

- Do not change application business logic or database models.
- Show at most one demo case per route.
- Keep all full test instructions in `docs/MANUAL_TEST_CASES.md`.
- Prefer simple dictionaries, one template include, and focused CSS.

---

### Task 1: Single-case context data

**Files:**
- Create: `tools/test_demo_card.py`
- Modify: `expensemate/demo_data.py`

**Interfaces:**
- Produces: `demo_test_data(request) -> {"demo_case": dict | None}`

- [ ] Write tests that require one dictionary per route and reject list-valued mappings.
- [ ] Run the tests and confirm they fail against the current list-based implementation.
- [ ] Replace `DEMO_CASES` with `DEMO_CASES_BY_ROUTE`, one case per route.
- [ ] Run the tests and confirm they pass.

### Task 2: Compact reusable card

**Files:**
- Modify: `templates/includes/demo_test_data.html`
- Modify: `static/css/expensemate.css`
- Modify: `tools/test_demo_card.py`

**Interfaces:**
- Consumes: `demo_case.id`, `demo_case.heading`, `demo_case.lines`

- [ ] Add tests that reject the old floating panel, loops over cases, and visible full-steps link.
- [ ] Run the tests and confirm they fail.
- [ ] Render one normal-flow `<aside>` with a concise heading and lines.
- [ ] Replace fixed overlay styles with a compact light-grey card.
- [ ] Run the tests and confirm they pass.

### Task 3: Screenshots and documentation

**Files:**
- Modify: `tools/render_screenshots.py`
- Modify: `README.md`
- Regenerate: `docs/screenshots/*.png`

**Interfaces:**
- Produces: README previews showing one compact demo card per screen.

- [ ] Update screenshot helper to draw one compact card instead of a multi-case overlay.
- [ ] Update README description of on-screen demo data.
- [ ] Regenerate screenshots.
- [ ] Run repository verification and static demo-card tests.
- [ ] Create the updated ZIP archive.
