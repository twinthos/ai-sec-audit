"""Current-package tests. Legacy Vercel tests in tests/ are pending migration."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

reader = load("twinthos_cli_reader", "scripts/cli_read.py")
renderer = load("twinthos_renderer", "scripts/render_report.py")

class PackageTests(unittest.TestCase):
    def test_skill_package_files_exist(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: twinthos-ai-sec-audit", skill)
        for path in ("references/checklist.md", "references/capabilities.md",
                     "references/report-model.md", "assets/report.html",
                     "assets/report.css", "scripts/cli_read.py",
                     "scripts/render_report.py", "scripts/check_report.py"):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())

    def test_allowed_commands_and_safe_metadata(self):
        self.assertIn("whoami", reader.ALLOWED_COMMANDS)
        self.assertNotIn("delete", reader.ALLOWED_COMMANDS)
        result = reader.filter_fields({
            "name": "test",
            "config": {"token": "SECRET", "name": "agent", "nested": {"password": "SHOULD_NOT_APPEAR"}},
            "tools": [{"name": "safe", "access_token": "ALSO_SECRET"}],
            "secret": "hidden",
            "stdout": "private shell output",
        }, reader.ALLOWED_COMMANDS["agent-get"]["fields"])
        output = json.dumps(result)
        for secret in ("SECRET", "SHOULD_NOT_APPEAR", "ALSO_SECRET", "private shell output"):
            self.assertNotIn(secret, output)

    def test_untrusted_markdown_is_escaped(self):
        payload = '<img src=x onerror=alert(1)>'
        html = renderer.md_to_html("# Title\n\n- " + payload + "\n\n| Field | Value |\n| --- | --- |\n| a | " + payload + " |")
        self.assertNotIn("<img", html)
        self.assertIn("&lt;img", html)

    def test_renderer_smoke(self):
        with tempfile.TemporaryDirectory() as d:
            inp = Path(d) / "security-audit.md"
            out = Path(d) / "report.html"
            inp.write_text("# Security Audit\n\n## Summary\n\nNo configuration changed.", encoding="utf-8")
            renderer.render(inp, out)
            body = out.read_text(encoding="utf-8")
            self.assertIn("Security Audit", body)
            self.assertIn("No configuration changed.", body)
            self.assertNotIn("{{content}}", body)

if __name__ == "__main__":
    unittest.main()
