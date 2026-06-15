import unittest
import argparse
import sys
from unittest.mock import patch
import os

# We mock the tools since they might not be fully structured for import yet
# Testing the argument parsing behavior is safe and reliable without deep imports.
class TestToolsCLI(unittest.TestCase):
    
    def test_vex_skill_gen_args(self):
        # Using subprocess to test CLI parsing behavior of vex-skill-gen.py
        import subprocess
        result = subprocess.run([sys.executable, "tools/vex-skill-gen.py", "-h"], capture_output=True, text=True)
        self.assertIn("generate", result.stdout)
        self.assertIn("list", result.stdout)
        
    def test_vex_cost_args(self):
        import subprocess
        result = subprocess.run([sys.executable, "tools/vex-cost.py", "-h"], capture_output=True, text=True)
        self.assertIn("report", result.stdout)
        self.assertIn("budget", result.stdout)
        
    def test_vex_memory_args(self):
        import subprocess
        result = subprocess.run([sys.executable, "tools/vex-memory.py", "-h"], capture_output=True, text=True)
        self.assertIn("scan", result.stdout)
        self.assertIn("search", result.stdout)

if __name__ == "__main__":
    unittest.main()
