import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_CLI = REPO_ROOT / "adapters" / "install_adapter.py"

REQUIRED_ADAPTERS = [
    "claude-code",
    "cursor",
    "codex",
    "gemini-cli",
    "copilot-cli",
    "opencode",
    "zed",
]


class TestAdapters(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(ADAPTER_CLI), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_all_required_adapter_configs_exist(self):
        for adapter in REQUIRED_ADAPTERS:
            path = REPO_ROOT / "adapters" / f"{adapter}.json"
            self.assertTrue(path.exists(), f"missing {path}")

    def test_adapter_config_schema_required_fields(self):
        for adapter in REQUIRED_ADAPTERS:
            payload = json.loads((REPO_ROOT / "adapters" / f"{adapter}.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["id"], adapter)
            self.assertIn("harness", payload)
            self.assertIn("version", payload)
            self.assertIn("fileMapping", payload)
            self.assertIn("features", payload)
            self.assertIn("install", payload)

    def test_list_outputs_supported_harnesses(self):
        result = self.run_cli("list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        ids = {item["id"] for item in payload["data"]["adapters"]}
        self.assertTrue(set(REQUIRED_ADAPTERS).issubset(ids))

    def test_install_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.run_cli("install", "cursor", "--target-dir", tmpdir, "--dry-run", "--json")
            created = list(Path(tmpdir).rglob("*"))

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(created, [])

    def test_unknown_adapter_errors_cleanly(self):
        result = self.run_cli("install", "unknown", "--dry-run", "--json")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("unknown adapter", payload["error"].lower())

    def test_rejects_path_traversal_target(self):
        result = self.run_cli("install", "cursor", "--target-dir", "..", "--dry-run", "--json")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("refusing", payload["error"].lower())


if __name__ == "__main__":
    unittest.main()
