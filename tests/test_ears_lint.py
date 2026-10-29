"""Regression tests for ears_lint. Run: python -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "ears-requirements"
sys.path.insert(0, str(SKILL / "scripts"))

import ears_lint as L  # noqa: E402


def rules(text):
    r = L.Requirement(rid="T", line=1, text=L.clean(text))
    L.lint(r)
    return r.pattern, {f.rule for f in r.findings}


class Patterns(unittest.TestCase):
    def test_classification(self):
        cases = {
            "The OLT shall encrypt downstream traffic with AES-128": "ubiquitous",
            "When an order arrives, the order manager shall acknowledge it within 2 s": "event",
            "While in maintenance mode, the OLT shall reject provisioning commands": "state",
            "If the link fails, then the router shall switch to the standby path within 50 ms": "unwanted",
            "Where dual-homing is licensed, the OLT shall protect each PON port": "optional",
            "While in maintenance mode, when a ticket arrives, the TT system shall tag it planned": "complex",
        }
        for text, expected in cases.items():
            pattern, found = rules(text)
            self.assertEqual(pattern, expected, text)
            self.assertFalse(found, f"{text}: {found}")


class Rules(unittest.TestCase):
    def check(self, text, rule):
        self.assertIn(rule, rules(text)[1], text)

    def test_structure(self):
        self.check("The system should support fast provisioning", "E001")
        self.check("If the link fails the router shall switch over within 50 ms", "E002")
        self.check("When X occurs, when Y occurs, the OLT shall reboot", "E003")
        self.check("The billing engine, when a CDR arrives, shall rate it within 15 min", "E004")
        self.check("When X, while Y, the OLT shall reboot", "E004")
        self.check("The OLT shall reboot. The ONT shall reboot", "E005")
        self.check("When an order arrives, the order manager shall validate it and store it", "E006")
        self.check("When X, if Y, then the OLT shall reboot", "E007")
        self.check("The charging system shall block the session when the balance reaches zero", "E008")
        self.check("WHEN the user submits the form THEN the order manager SHALL save the record", "E009")

    def test_testability(self):
        self.check("The portal shall respond quickly", "E101")
        self.check("The portal shall export CSV, PDF, etc", "E102")
        self.check("The portal shall support bulk upload", "E103")
        self.check("Errors shall be logged", "E104")
        self.check("The ONT shall not drop frames", "E105")
        self.check("When an order arrives, the system shall acknowledge it within 2 s", "E106")
        self.check("The system should support fast provisioning", "E106")
        self.check("The system should support fast provisioning", "E101")
        self.check("When the account manager changes any quote item, the CPQ system shall create a new quote version", "E107")

    def test_slide_example(self):
        _, found = rules("While a quote is approved, When the account manager changes any quote item, "
                         "the CPQ system shall create a new quote version and restart approval")
        self.assertEqual(found, {"E006", "E107"})

    def test_no_false_conjunction(self):
        self.assertNotIn("E006", rules("When 8 or more alarms arrive, the platform shall raise 1 alarm")[1])

    def test_ignore_marker(self):
        r = L.make("T", 1, "When X, the OLT shall reboot and log ears-ignore: E006")
        L.lint(r)
        self.assertNotIn("E006", {f.rule for f in r.findings})


class Files(unittest.TestCase):
    def test_examples_clean(self):
        path = SKILL / "references" / "telecom-examples.md"
        self.assertEqual(L.main([str(path), "--strict", "--quiet"]), 0)

    def test_user_story_example_clean(self):
        path = SKILL / "templates" / "user-story.md"
        reqs = [r for r in L.parse_markdown(path.read_text().splitlines()) if r.rid.startswith("CPQ")]
        self.assertEqual(len(reqs), 4)
        for r in reqs:
            L.lint(r)
            self.assertFalse(r.findings, f"{r.rid}: {r.findings}")

    def test_set_level_fault_gap(self):
        reqs = [L.Requirement("A", 1, "When X, the OLT shall reboot")]
        L.lint(reqs[0])
        self.assertEqual([f.rule for f in L.lint_set(reqs)], ["E201"])

    def test_markdown_table_parse(self):
        lines = ["| ID | Requirement |", "|---|---|", "| FUL-1 | When X, the OLT shall reboot. |"]
        reqs = L.parse_markdown(lines)
        self.assertEqual((reqs[0].rid, reqs[0].text), ("FUL-1", "When X, the OLT shall reboot"))


if __name__ == "__main__":
    unittest.main()
