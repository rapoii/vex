import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "vex_hooks.py"
PROFILES = REPO_ROOT / "hooks" / "profiles.json"


class TestHookProfiles(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env = {**os.environ, "VEX_HOME": str(Path(self.temp_dir.name) / "home")}

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=self.env)

    def test_profiles_file_contains_required_profiles(self):
        data = json.loads(PROFILES.read_text(encoding="utf-8"))
        self.assertIn("minimal", data["profiles"])
        self.assertIn("standard", data["profiles"])
        self.assertIn("strict", data["profiles"])
        self.assertIn("custom", data["profiles"])

    def test_profile_list_returns_profiles(self):
        result = self.run_cli(["profile", "list", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("standard", payload["data"]["profiles"])

    def test_set_profile_writes_runtime_control_file(self):
        result = self.run_cli(["profile", "set", "strict", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        runtime = Path(self.env["VEX_HOME"]) / "hook-runtime.json"
        self.assertEqual(json.loads(runtime.read_text(encoding="utf-8"))["profile"], "strict")

    def test_disable_hook_adds_runtime_disabled_hook(self):
        result = self.run_cli(["disable", "check-file-size", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        runtime = Path(self.env["VEX_HOME"]) / "hook-runtime.json"
        self.assertIn("check-file-size", json.loads(runtime.read_text(encoding="utf-8"))["disabled_hooks"])

    def test_env_disabled_hooks_remove_hook_from_resolved_profile(self):
        env = {**self.env, "VEX_DISABLED_HOOKS": "check-file-size"}
        result = subprocess.run([sys.executable, str(SCRIPT), "profile", "show", "standard", "--json"], capture_output=True, text=True, env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        hook_ids = [hook["name"] for group in payload["data"]["hooks"].values() for hook in group]
        self.assertNotIn("check-file-size", hook_ids)


if __name__ == "__main__":
    unittest.main()
