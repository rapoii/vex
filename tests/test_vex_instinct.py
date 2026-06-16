import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "vex_instinct.py"


class TestVexInstinct(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name) / "home"
        self.home.mkdir()
        self.env = {**os.environ, "VEX_HOME": str(self.home)}

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def seed_db(self):
        sessions_script = REPO_ROOT / "tools" / "vex_sessions.py"
        logs = Path(self.temp_dir.name) / "logs"
        logs.mkdir()
        (logs / "one.jsonl").write_text(
            "\n".join([
                json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:00:00Z", "type": "session_start", "project": "vex"}),
                json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:01:00Z", "type": "tool_call", "tool": "Read", "success": True}),
                json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:02:00Z", "type": "tool_call", "tool": "Edit", "success": True}),
                json.dumps({"session_id": "s1", "timestamp": "2026-06-16T10:03:00Z", "type": "tool_call", "tool": "Bash", "success": True}),
            ]),
            encoding="utf-8",
        )
        subprocess.run([sys.executable, str(sessions_script), "record", "--session-dir", str(logs), "--json"], env=self.env, check=True, capture_output=True, text=True)

    def test_learn_extracts_repeated_tool_pattern(self):
        self.seed_db()

        result = self.run_cli(["learn", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload["data"]["learned"], 1)
        instincts_file = self.home / "vex-instincts.json"
        self.assertTrue(instincts_file.exists())

    def test_list_shows_confidence_scores(self):
        self.seed_db()
        self.run_cli(["learn", "--json"])

        result = self.run_cli(["list", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("confidence", payload["data"]["instincts"][0])

    def test_forget_removes_instinct(self):
        self.seed_db()
        learn = self.run_cli(["learn", "--json"])
        instinct_id = json.loads(learn.stdout)["data"]["instincts"][0]["id"]

        result = self.run_cli(["forget", instinct_id, "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        listed = json.loads(self.run_cli(["list", "--json"]).stdout)["data"]["instincts"]
        self.assertFalse(any(item["id"] == instinct_id for item in listed))

    def test_apply_writes_high_confidence_rule(self):
        data = {"instincts": [{"id": "tool-read-edit-bash", "title": "Use Read before Edit then Bash", "confidence": 0.91, "kind": "tool_sequence", "rule": "Read before Edit, validate with Bash.", "evidence": {}}]}
        (self.home / "vex-instincts.json").write_text(json.dumps(data), encoding="utf-8")

        result = self.run_cli(["apply", "--json", "--output-dir", str(Path(self.temp_dir.name) / "rules")])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["applied"], 1)


if __name__ == "__main__":
    unittest.main()
