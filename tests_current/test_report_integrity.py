"""Current-package regression tests for report integrity and privacy boundaries."""
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


manage = module("audit_manage_report_current", "scripts/manage_report.py")
checker = module("audit_check_report_current", "scripts/check_report.py")
renderer = module("audit_render_report_current", "scripts/render_report.py")


def observation(topic="IAM-01", status="satisfactory", scope="demo-project"):
    return {
        "topic_id": topic, "scope_alias": scope,
        "observed_at": "2026-11-03T08:00:00+00:00",
        "source_kind": "synthetic_fixture",
        "status": status,
        "rationale": "Invented metadata only. No real account was read.",
    }


class ReportIntegrityTests(unittest.TestCase):
    def test_24_core_and_four_unique_optional_ids(self):
        ids = manage.ALL_IDS
        self.assertEqual(len(manage.CORE_IDS), 24)
        self.assertEqual(len(manage.OPTIONAL_IDS), 4)
        self.assertEqual(len(ids), len(set(ids)), "Optional IDs must not collide with core IDs")
        source = (ROOT / "references/checklist.md").read_text(encoding="utf-8")
        headings = re.findall(r"^### ([A-Z]{3}-\d{2})\s+-", source, re.M)
        self.assertEqual(set(ids), set(headings))
        self.assertEqual(len(headings), 28, "Each checklist ID must be defined exactly once")

    def test_revision_two_and_numeric_latest_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model.json"
            output = Path(folder) / "report.md"
            rev1 = manage.append_revision(model, [observation("IAM-01")], "demo-project")
            rev2 = manage.append_revision(model, [observation("SRC-02", "action_recommended")], "demo-project")
            self.assertEqual((rev1["revision"], rev2["revision"]), (1, 2))
            for i in range(3, 12):
                manage.append_revision(model, [observation("SRC-02", "action_recommended")], "demo-project")
            manage.rebuild_markdown(model, output)
            text = output.read_text()
            self.assertIn("| SRC-02 | demo-project | | action_recommended |", text)
            self.assertIn("| IAM-01 | demo-project | | not_reviewed |", text)
            self.assertIn("## Appendix: check outcomes", text)
            self.assertIn("### OPS-04 - Review outcome", text)
            self.assertEqual(manage._latest_revision(manage.load_model(model))["revision"], 11)

    def test_scope_mismatch_duplicate_and_nonobject_denied(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model.json"
            with self.assertRaises(ValueError):
                manage.append_revision(model, [observation(scope="different")], "demo-project")
            with self.assertRaises(ValueError):
                manage.append_revision(model, [observation(), observation()], "demo-project")
            self.assertTrue(manage.validate_observation("untrusted"))
            self.assertFalse(model.exists(), "Validation must happen before the model is written")

    def test_obvious_credential_patterns_refused(self):
        item = observation()
        item["rationale"] = "Synthetic invalid key: " + "AKIA" + "Z" * 16
        self.assertTrue(any("credential" in error.lower() for error in manage.validate_observation(item)))

    def test_rendered_html_parity_and_passivity(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model.json"
            markdown = Path(folder) / "report.md"
            rendered = Path(folder) / "report.html"
            manage.append_revision(model, [observation("IAM-01"), observation("SRC-02", "needs_confirmation")], "demo-project")
            manage.rebuild_markdown(model, markdown)
            renderer.render(markdown, rendered)
            html = rendered.read_text(encoding="utf-8")
            self.assertFalse(checker.check_heading_structure(html))
            self.assertFalse(checker.check_check_count(html))
            self.assertFalse(checker.check_status_matrix_parity(html))
            self.assertFalse(checker.check_passive_html(html))
            process = subprocess.run([sys.executable, str(ROOT / "scripts/check_report.py"), str(rendered)],
                                     capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_report_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model.json"
            markdown = Path(folder) / "report.md"
            rendered = Path(folder) / "report.html"
            manage.append_revision(model, [observation()], "demo-project")
            manage.rebuild_markdown(model, markdown)
            renderer.render(markdown, rendered)
            html = rendered.read_text(encoding="utf-8")
            modified = html.replace('status-satisfactory', 'status-not_reviewed', 1).replace('>satisfactory</span>', '>not_reviewed</span>', 1)
            self.assertTrue(checker.check_status_matrix_parity(modified))
            self.assertTrue(checker.check_check_count(html.replace("IAM-01 - Review outcome", "ZZZ-99 - Review outcome", 1)))

    def test_escaped_injection_is_not_executable(self):
        with tempfile.TemporaryDirectory() as folder:
            model = Path(folder) / "model.json"
            markdown = Path(folder) / "report.md"
            rendered = Path(folder) / "report.html"
            item = observation()
            item["rationale"] = '<img src=x onerror=alert(1)>'
            manage.append_revision(model, [item], "demo-project")
            manage.rebuild_markdown(model, markdown)
            renderer.render(markdown, rendered)
            html = rendered.read_text()
            self.assertIn("&lt;img", html)
            self.assertFalse(checker.check_passive_html(html))
            self.assertTrue(checker.check_passive_html('<img src="x" onerror="alert(1)">'))


if __name__ == "__main__":
    unittest.main()
