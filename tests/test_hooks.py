import unittest
import os
import subprocess
import sys
import json

class TestHooks(unittest.TestCase):
    
    def test_check_file_size_rejection(self):
        payload = {"tool_input": {"file_path": "test.py", "content": "a\n" * 600_000}}
        result = subprocess.run(
            [sys.executable, "hooks/scripts/check-file-size.py"], 
            input=json.dumps(payload), 
            text=True, 
            capture_output=True
        )
        self.assertEqual(result.returncode, 1, f"Should exit 1 for large file. Stderr: {result.stderr}")
        self.assertIn("BLOCKED", result.stderr)

    def test_check_file_size_allow(self):
        payload = {"tool_input": {"file_path": "test.py", "content": "a\n" * 100}}
        result = subprocess.run(
            [sys.executable, "hooks/scripts/check-file-size.py"], 
            input=json.dumps(payload), 
            text=True, 
            capture_output=True
        )
        self.assertEqual(result.returncode, 0, f"Should exit 0 for small file. Stderr: {result.stderr}")

if __name__ == "__main__":
    unittest.main()
