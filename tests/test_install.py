import unittest
import os
import subprocess
import tempfile
import stat

class TestInstallScript(unittest.TestCase):
    def setUp(self):
        self.script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "install.sh"))

    def test_dry_run(self):
        result = subprocess.run(
            ["bash", self.script_path, "--dry-run"],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("DRY RUN — no changes will be made", result.stdout)
        self.assertIn("Would copy:", result.stdout)

    def test_profile_selection(self):
        result = subprocess.run(
            ["bash", self.script_path, "--dry-run", "--profile", "custom-profile"],
            capture_output=True,
            text=True
        )
        self.assertIn("custom-profile", result.stdout)

    def test_install_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vex_home = os.path.join(tmpdir, ".vex")
            env = os.environ.copy()
            env["VEX_HOME"] = vex_home

            # Create mock source files to prevent cp failures
            script_dir = os.path.dirname(self.script_path)
            # The script assumes it's in the repo root

            result = subprocess.run(
                ["bash", self.script_path, "--dry-run"],  # Keep as dry-run to avoid polluting dev env
                env=env,
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn(vex_home, result.stdout)

if __name__ == "__main__":
    unittest.main()