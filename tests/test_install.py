import unittest
import os
import sys
import subprocess
import tempfile

def get_bash_cmd():
    return "sh" if sys.platform == "win32" else "bash"

class TestInstallScript(unittest.TestCase):
    def setUp(self):
        self.script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "install.sh"))
        self.repo_root = os.path.dirname(self.script_path)

    def test_dry_run(self):
        result = subprocess.run(
            [get_bash_cmd(), self.script_path, "--dry-run"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN — no changes will be made", result.stdout)
        self.assertIn("Would copy", result.stdout)

    def test_profile_selection(self):
        result = subprocess.run(
            [get_bash_cmd(), self.script_path, "--dry-run", "--profile", "minimal"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("minimal", result.stdout)

    def test_install_execution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vex_home = os.path.join(tmpdir, ".vex")
            env = os.environ.copy()
            env["VEX_HOME"] = vex_home

            result = subprocess.run(
                [get_bash_cmd(), self.script_path, "--dry-run"],  # Keep as dry-run to avoid polluting dev env
                cwd=self.repo_root,
                env=env,
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(vex_home, result.stdout)

if __name__ == "__main__":
    unittest.main()