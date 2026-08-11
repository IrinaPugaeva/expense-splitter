#!/usr/bin/env python3
"""Regression checks for the compact, single demo-case card."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def load_demo_data_module():
    path = ROOT / "expensemate" / "demo_data.py"
    spec = importlib.util.spec_from_file_location("expensemate_demo_data", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DemoDataTests(unittest.TestCase):
    def test_every_route_has_exactly_one_demo_case_dictionary(self):
        module = load_demo_data_module()
        mapping = module.DEMO_CASES_BY_ROUTE

        self.assertGreater(len(mapping), 0)
        for route_name, case in mapping.items():
            with self.subTest(route_name=route_name):
                self.assertIsInstance(case, dict)
                self.assertEqual(set(case), {"id", "heading", "lines"})
                self.assertTrue(case["id"])
                self.assertTrue(case["heading"])
                self.assertIsInstance(case["lines"], list)
                self.assertGreater(len(case["lines"]), 0)

    def test_context_processor_returns_demo_case_not_case_list(self):
        module = load_demo_data_module()
        request = SimpleNamespace(resolver_match=SimpleNamespace(url_name="login"))

        context = module.demo_test_data(request)

        self.assertEqual(context["demo_case"], module.DEMO_CASES_BY_ROUTE["login"])
        self.assertNotIn("demo_cases", context)

    def test_unknown_route_returns_none(self):
        module = load_demo_data_module()
        request = SimpleNamespace(resolver_match=SimpleNamespace(url_name="not-a-route"))

        self.assertEqual(module.demo_test_data(request), {"demo_case": None})


class DemoCardMarkupTests(unittest.TestCase):
    def test_template_renders_one_case_without_full_steps_or_case_loop(self):
        template = (ROOT / "templates" / "includes" / "demo_test_data.html").read_text()

        self.assertIn("{% if demo_case %}", template)
        self.assertIn('class="demo-data-card"', template)
        self.assertIn('data-test-case="{{ demo_case.id }}"', template)
        self.assertIn("{{ demo_case.heading }}", template)
        self.assertNotIn("demo_cases", template)
        self.assertNotIn("{% for case", template)
        self.assertNotIn("Full steps", template)
        self.assertNotIn("MANUAL_TEST_CASES", template)

    def test_public_auth_cards_embed_the_demo_card_once(self):
        include = '{% include "includes/demo_test_data.html" %}'
        base = (ROOT / "templates" / "base.html").read_text()
        self.assertEqual(base.count(include), 1)

        for relative_path in [
            "templates/accounts/login.html",
            "templates/accounts/register.html",
            "templates/accounts/password_reset.html",
            "templates/accounts/password_reset_confirm.html",
        ]:
            with self.subTest(template=relative_path):
                template = (ROOT / relative_path).read_text()
                self.assertEqual(template.count(include), 1)

    def test_card_is_normal_flow_not_fixed_overlay(self):
        css = (ROOT / "static" / "css" / "expensemate.css").read_text()

        self.assertIn(".demo-data-card", css)
        self.assertIn(".demo-data-card code", css)
        self.assertNotRegex(
            css,
            r"\.demo-data-card\s*\{[^}]*position\s*:\s*fixed",
        )
        self.assertNotIn(".demo-test-panel", css)


class ScreenshotGeneratorTests(unittest.TestCase):
    def test_screenshot_generator_uses_one_compact_demo_card(self):
        source = (ROOT / "tools" / "render_screenshots.py").read_text()

        self.assertIn("def demo_card(", source)
        self.assertNotIn("def test_panel(", source)
        self.assertNotIn("DEMO TEST DATA", source)
        self.assertNotIn("docs/MANUAL_TEST_CASES.md", source)
        self.assertNotRegex(source, r"demo_card\([^\n]*\[\(")



if __name__ == "__main__":
    unittest.main()
