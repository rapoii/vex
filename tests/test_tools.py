import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add tools dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from tools from tools import vex_cost
from tools from tools import vex_skill_gen
from tools from tools import vex_memory

class TestVexCost(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vex_dir = os.path.join(self.temp_dir.name, ".vex")
        os.environ["VEX_HOME"] = self.vex_dir

    def tearDown(self):
        self.temp_dir.cleanup()
        if "VEX_HOME" in os.environ:
            del os.environ["VEX_HOME"]

    @patch('tools.vex_cost.find_session_files')
    def test_cmd_report(self, mock_find):
        # Create dummy session file
        session_file = os.path.join(self.temp_dir.name, "session.jsonl")
        with open(session_file, "w") as f:
            f.write(json.dumps({"type": "usage", "model": "claude-3-opus-20240229", "input_tokens": 1000, "output_tokens": 500}) + "\n")
            f.write(json.dumps({"type": "usage", "model": "claude-3-sonnet-20240229", "input_tokens": 2000, "output_tokens": 1000}) + "\n")

        mock_find.return_value = [session_file]

        args = MagicMock()
        args.project = None
        args.days = 30
        args.json = True

        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
            vex_cost.cmd_report(args)
            output = "".join([call[0][0] for call in mock_stdout.write.call_args_list])

        data = json.loads(output)
        self.assertIn("total_cost", data)
        self.assertIn("models", data)
        self.assertTrue(len(data["models"]) > 0)

    def test_compute_cost(self):
        # Test opus cost computation (15/M input, 75/M output)
        cost = vex_cost.compute_cost("claude-3-opus-20240229", 1000000, 1000000)
        self.assertAlmostEqual(cost, 90.0)

        # Test fallback
        cost2 = vex_cost.compute_cost("unknown-model", 1000000, 1000000)
        self.assertGreater(cost2, 0)

    @patch('tools.vex_cost.ensure_vex_dir')
    def test_budget(self, mock_ensure):
        mock_ensure.return_value = self.vex_dir
        os.makedirs(self.vex_dir, exist_ok=True)

        # Test Set
        args_set = MagicMock()
        args_set.amount = 50.0

        with patch('sys.stdout', new_callable=MagicMock):
            vex_cost.cmd_budget_set(args_set)

        budget_file = os.path.join(self.vex_dir, "budget.json")
        self.assertTrue(os.path.exists(budget_file))

        # Test Status
        args_status = MagicMock()
        args_status.project = None
        args_status.days = 30

        with patch('sys.stdout', new_callable=MagicMock) as mock_stdout:
            with patch('vex_cost.find_session_files', return_value=[]):
                vex_cost.cmd_budget_status(args_status)

        output = "".join([call[0][0] for call in mock_stdout.write.call_args_list])
        self.assertIn("50.0", output)

class TestVexSkillGen(unittest.TestCase):
    def test_extract_tool_calls(self):
        entries = [
            {"type": "message", "role": "user", "content": "hello"},
            {"type": "tool_call", "name": "Bash", "input": {"command": "ls"}},
            {"type": "tool_call", "name": "Write", "input": {"file_path": "test.txt", "content": "hi"}},
            {"type": "tool_call", "name": "Bash", "input": {"command": "cat test.txt"}}
        ]
        calls = vex_skill_gen.extract_tool_calls(entries)
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0], "Bash")
        self.assertEqual(calls[1], "Write")

    def test_find_patterns(self):
        calls = ["Bash", "Write", "Bash", "Bash", "Write", "Bash", "Read", "Bash", "Write", "Bash"]
        patterns = vex_skill_gen.find_patterns(calls, min_occurrences=2)
        # Should find 'Bash, Write, Bash'
        self.assertTrue(any(p["pattern"] == ["Bash", "Write", "Bash"] for p in patterns))

    def test_generate_skill_md(self):
        pattern = ["Bash", "Write", "Bash"]
        md = vex_skill_gen.generate_skill_md("test-skill", pattern, 5, ["test.txt"], ["topic1"], 90.0, "proj1")
        self.assertIn("test-skill", md)
        self.assertIn("Bash -> Write -> Bash", md)
        self.assertIn("topic1", md)

class TestVexMemory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vex_dir = os.path.join(self.temp_dir.name, ".vex")
        os.environ["VEX_HOME"] = self.vex_dir
        os.makedirs(self.vex_dir, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()
        if "VEX_HOME" in os.environ:
            del os.environ["VEX_HOME"]

    @patch('tools.vex_memory.ensure_vex_dir')
    def test_save_load_graph(self, mock_ensure):
        mock_ensure.return_value = self.vex_dir
        graph = {"files": {"test.txt": {"mentions": 5}}}
        vex_memory.save_graph(graph)

        loaded = vex_memory.load_graph()
        self.assertEqual(loaded["files"]["test.txt"]["mentions"], 5)

    def test_extract_files_mentioned(self):
        entries = [
            {"type": "tool_call", "name": "Write", "input": {"file_path": "/path/to/test.txt"}},
            {"type": "tool_call", "name": "Read", "input": {"file_path": "/path/to/test.txt"}},
            {"type": "message", "role": "assistant", "content": "I edited test.txt."}
        ]
        files = vex_memory.extract_files_mentioned(entries)
        self.assertIn("test.txt", files)

    @patch('tools.vex_memory.find_session_files')
    @patch('tools.vex_memory.ensure_vex_dir')
    def test_cmd_scan(self, mock_ensure, mock_find):
        mock_ensure.return_value = self.vex_dir

        session_file = os.path.join(self.temp_dir.name, "session.jsonl")
        with open(session_file, "w") as f:
            f.write(json.dumps({"type": "tool_call", "name": "Write", "input": {"file_path": "app.py"}}) + "\n")

        mock_find.return_value = [session_file]

        args = MagicMock()
        args.project = None
        args.force = True

        with patch('sys.stdout', new_callable=MagicMock):
            vex_memory.cmd_scan(args)

        graph = vex_memory.load_graph()
        self.assertIn("app.py", graph.get("files", {}))

if __name__ == "__main__":
    unittest.main()