import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "vex_optimize.py"


class TestVexOptimize(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env = {**os.environ, "VEX_HOME": str(Path(self.temp_dir.name) / "home")}

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=self.env)

    def test_slim_removes_filler_words(self):
        result = self.run_cli(["slim", "Please just really help me implement a comprehensive solution", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertLess(payload["data"]["after_words"], payload["data"]["before_words"])
        self.assertNotIn("really", payload["data"]["prompt"])

    def test_suggest_routes_architecture_to_opus(self):
        result = self.run_cli(["suggest", "--task", "design architecture migration plan", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["model"], "opus")

    def test_suggest_routes_exploration_to_haiku(self):
        result = self.run_cli(["suggest", "--task", "search files and classify simple logs", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["model"], "haiku")

    def test_analyze_reads_session_database(self):
        db = Path(self.temp_dir.name) / "home" / "vex-sessions.db"
        db.parent.mkdir()
        sessions_script = REPO_ROOT / "tools" / "vex_sessions.py"
        logs = Path(self.temp_dir.name) / "logs"
        logs.mkdir()
        (logs / "one.jsonl").write_text("\n".join([
            json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:00:00Z", "type": "session_start"}),
            json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:01:00Z", "type": "usage", "input_tokens": 120, "output_tokens": 30, "cost_usd": 0.02}),
        ]), encoding="utf-8")
        subprocess.run([sys.executable, str(sessions_script), "record", "--session-dir", str(logs), "--json"], env=self.env, check=True, capture_output=True, text=True)

        result = self.run_cli(["analyze", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["tokens_total"], 150)


if __name__ == "__main__":
    unittest.main()
