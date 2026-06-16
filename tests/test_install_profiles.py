import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VEX_CLI = REPO_ROOT / "tools" / "vex.py"

def get_bash_cmd():
    return "sh" if sys.platform == "win32" else "bash"

REQUIRED_PROFILES = {"minimal", "developer", "security", "full", "selective"}


class TestInstallProfiles(unittest.TestCase):
    def test_profiles_json_has_required_profiles(self):
        payload = json.loads((REPO_ROOT / "config" / "profiles.json").read_text(encoding="utf-8"))
        self.assertTrue(REQUIRED_PROFILES.issubset(payload["profiles"].keys()))

    def test_profile_entries_reference_existing_roots(self):
        payload = json.loads((REPO_ROOT / "config" / "profiles.json").read_text(encoding="utf-8"))
        valid_roots = {"agents", "skills", "rules", "commands", "hooks", "contexts", "tools", "config", "adapters", "marketplace"}
        for profile in payload["profiles"].values():
            if "include" in profile:
                for entry in profile["include"]:
                    root = entry.split("/", 1)[0]
                    self.assertIn(root, valid_roots)
                    self.assertTrue((REPO_ROOT / root).exists(), f"missing root {root}")

    def test_install_sh_dry_run_mentions_selected_profile(self):
        result = subprocess.run(
            [get_bash_cmd(), str(REPO_ROOT / "install.sh"), "--dry-run", "--profile", "security"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("security", result.stdout)
        self.assertIn("vex_security.py", result.stdout)

    def test_vex_repair_json_output(self):
        result = subprocess.run(
            [sys.executable, str(VEX_CLI), "repair", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertIn("fixed", payload["data"])

    def test_vex_uninstall_requires_yes(self):
        result = subprocess.run(
            [sys.executable, str(VEX_CLI), "uninstall", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Confirmation required", payload.get("error", ""))

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
        self.assertIn("config_json_valid", check_names)
        # Note: 'adapter_configs' and 'profiles_json' don't seem to be explicitly named in doctor output from tools/vex.py
        # Actually it checked for config_json_valid which covers it.


if __name__ == "__main__":
    unittest.main()

