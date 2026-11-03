"""Current-package regression tests for read-only CLI argument boundaries."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_cli_reader_hardening", ROOT / "scripts/cli_read.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class CliBoundaryTests(unittest.TestCase):
    def test_allows_only_selected_read_flags_and_one_identifier(self):
        self.assertTrue(reader.safe_cli_args([]))
        self.assertTrue(reader.safe_cli_args(["--scope", "company-1", "--agent", "agent_3"]))
        self.assertTrue(reader.safe_cli_args(["--project", "legal/case-review"]))
        self.assertTrue(reader.safe_cli_args(["agent-42"]))
        self.assertFalse(reader.safe_cli_args(["--unknown"]))
        self.assertFalse(reader.safe_cli_args(["--delete"]))
        self.assertFalse(reader.safe_cli_args(["--scope", "--force"]))
        self.assertFalse(reader.safe_cli_args(["--scope", "one", "--scope", "two"]))
        self.assertFalse(reader.safe_cli_args(["--agent", "../secrets"]))
        self.assertFalse(reader.safe_cli_args(["first", "second"]))
        self.assertFalse(reader.safe_cli_args(["agent", ";echo"]))
        self.assertFalse(reader.safe_cli_args([None]))

    def test_invalid_input_is_rejected_before_calling_cli(self):
        with patch.object(reader, "check_cli_installed") as installed, \
             patch.object(reader.subprocess, "run") as run:
            self.assertEqual(
                reader.run_command("agent-get", ["--delete"])["error_code"],
                "invalid_cli_arguments",
            )
            self.assertEqual(
                reader.run_command("unsafe-mutate", [])["error_code"],
                "invalid_cli_arguments",
            )
            installed.assert_not_called()
            run.assert_not_called()

    def test_valid_scoped_command_never_uses_shell(self):
        from unittest.mock import Mock
        result = Mock(returncode=0, stdout='{"agent_id":"agent42","name":"Example"}')
        with patch.object(reader, "check_cli_installed", return_value=True), \
             patch.object(reader.subprocess, "run", return_value=result) as runner:
            output = reader.run_command("agent-get", ["--agent", "agent42"])
            self.assertEqual(output["agent_id"], "agent42")
            args, kwargs = runner.call_args
            self.assertEqual(args[0], ["twinthos", "agent-get", "--agent", "agent42"])
            self.assertNotIn("shell", kwargs)
            self.assertEqual(kwargs["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
