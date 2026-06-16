import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VEX_CLI = REPO_ROOT / "tools" / "vex.py"

REQUIRED_PROFILES = {"minimal", "developer", "security", "full", "selective"}


class TestInstallProfiles(unittest.TestCase):
    def test_profiles_json_has_required_profiles(self):
        payload = json.loads((REPO_ROOT / "config" / "profiles.json").read_text(encoding="utf-8"))
        self.assertTrue(REQUIRED_PROFILES.issubset(payload["profiles"].keys()))

    def test_profile_entries_reference_existing_roots(self):
        payload = json.loads((REPO_ROOT / "config" / "profiles.json").read_text(encoding="utf-8"))
        valid_roots = {"agents", "skills", "rules", "commands", "hooks", "contexts", "tools", "config", "adapters"}
        for profile in payload["profiles"].values():
            for entry in profile["include"]:
                root = entry.split("/", 1)[0]
                self.assertIn(root, valid_roots)
                self.assertTrue((REPO_ROOT / root).exists(), f"missing root {root}")

    def test_install_sh_dry_run_mentions_selected_profile(self):
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "install.sh"), "--dry-run", "--profile", "security"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("security", result.stdout)
        self.assertIn("vex_security.py", result.stdout)

    def test_vex_repair_and_uninstall_dry_run_return_plan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for command in ("repair", "uninstall"):
                result = subprocess.run(
                    [sys.executable, str(VEX_CLI), command, "--dry-run", "--target-dir", tmpdir, "--json"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["ok"])
                self.assertIn("actions", payload["data"])

    def test_vex_doctor_checks_profiles_and_adapters(self):
        result = subprocess.run(
            [sys.executable, str(VEX_CLI), "doctor", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        check_names = {check["name"] for check in payload["data"]["checks"]}
        self.assertIn("profiles_json", check_names)
        self.assertIn("adapter_configs", check_names)


if __name__ == "__main__":
    unittest.main()
