import csv
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tools" / "vex_sessions.py"


class TestVexSessions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.home = Path(self.temp_dir.name) / "home"
        self.logs = Path(self.temp_dir.name) / "logs"
        self.home.mkdir()
        self.logs.mkdir()
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

    def write_session(self):
        path = self.logs / "session.jsonl"
        rows = [
            {"session_id": "s1", "timestamp": "2026-06-16T10:00:00Z", "type": "session_start", "project": "vex", "model": "claude-opus-4-6"},
            {"session_id": "s1", "timestamp": "2026-06-16T10:01:00Z", "type": "tool_call", "tool": "Write", "input": {"file_path": "tools/example.py"}, "output": "ok", "success": True},
            {"session_id": "s1", "timestamp": "2026-06-16T10:02:00Z", "type": "usage", "input_tokens": 100, "output_tokens": 50, "cost_usd": 0.01},
            {"session_id": "s1", "timestamp": "2026-06-16T10:03:00Z", "type": "file_change", "path": "tools/example.py", "action": "write"},
            {"session_id": "s1", "timestamp": "2026-06-16T10:04:00Z", "type": "session_end"},
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n{bad json}\n", encoding="utf-8")
        return path

    def test_record_latest_sessions_creates_sqlite_tables(self):
        self.write_session()
        result = self.run_cli(["record", "--session-dir", str(self.logs), "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["sessions"], 1)
        self.assertEqual(payload["data"]["malformed_lines"], 1)

        db_path = self.home / "vex-sessions.db"
        with sqlite3.connect(db_path) as conn:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"sessions", "events", "files_changed"}.issubset(tables))

    def test_list_filters_by_project(self):
        self.write_session()
        self.run_cli(["record", "--session-dir", str(self.logs), "--json"])

        result = self.run_cli(["list", "--project", "vex", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["sessions"][0]["id"], "s1")

    def test_stats_returns_aggregate_usage(self):
        self.write_session()
        self.run_cli(["record", "--session-dir", str(self.logs), "--json"])

        result = self.run_cli(["stats", "--json"])

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["data"]["tokens_in"], 100)
        self.assertEqual(payload["data"]["tokens_out"], 50)

    def test_raw_query_rejects_non_select(self):
        result = self.run_cli(["query", "DELETE FROM sessions", "--json"])

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["error"]["code"], "QUERY_NOT_ALLOWED")

    def test_export_csv_outputs_rows(self):
        self.write_session()
        self.run_cli(["record", "--session-dir", str(self.logs), "--json"])

        result = self.run_cli(["export", "--format", "csv"])

        self.assertEqual(result.returncode, 0, result.stderr)
        rows = list(csv.DictReader(result.stdout.splitlines()))
        self.assertEqual(rows[0]["id"], "s1")


if __name__ == "__main__":
    unittest.main()
