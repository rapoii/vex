import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SECURITY_CLI = REPO_ROOT / "tools" / "vex_security.py"


class TestVexSecurity(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SECURITY_CLI), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_lists_102_rule_categories(self):
        result = self.run_cli("list-rules", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(len(payload["data"]["rules"]), 102)

    def test_rejects_invalid_target(self):
        result = self.run_cli("scan", "--target", "../agents")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_detects_secret_without_echoing_value(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "agents"
            agent_dir.mkdir()
            (agent_dir / "leaky.md").write_text('token = "sk-test-secretvalue1234567890"\n', encoding="utf-8")
            result = self.run_cli("scan", "--target", "agents", "--root", tmpdir, "--json")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        finding = payload["data"]["findings"][0]
        self.assertIn("secret", finding["rule_id"])
        self.assertNotIn("sk-test-secretvalue1234567890", json.dumps(payload))

    def test_detects_hook_injection_pattern(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hook_dir = Path(tmpdir) / "hooks"
            hook_dir.mkdir()
            (hook_dir / "hooks.json").write_text(
                json.dumps({"hooks": [{"command": "python x.py $USER_INPUT"}]}),
                encoding="utf-8",
            )
            result = self.run_cli("scan", "--target", "hooks", "--root", tmpdir, "--json")

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertTrue(any(item["severity"] in {"HIGH", "CRITICAL"} for item in payload["data"]["findings"]))

    def test_fail_on_threshold_controls_exit_code(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir) / "skills"
            skills_dir.mkdir()
            (skills_dir / "external.md").write_text("Fetch http://example.com/data without validation\n", encoding="utf-8")
            result = self.run_cli("scan", "--target", "skills", "--root", tmpdir, "--fail-on", "critical")

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
