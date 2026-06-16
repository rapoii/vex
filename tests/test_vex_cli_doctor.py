import json
import pytest
import subprocess
from pathlib import Path

VEX_CLI = Path(__file__).parent.parent / "tools" / "vex.py"
REPO_ROOT = Path(__file__).parent.parent

def run_vex(*args):
    return subprocess.run(["python", str(VEX_CLI), *args], capture_output=True, text=True)

def test_doctor_command():
    result = run_vex("doctor", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["command"] == "doctor"
    checks = {c["name"]: c["ok"] for c in data["data"]["checks"]}
    
    # Assert new checks added
    expected_checks = [
        "claude_dir_exists",
        "AGENTS_md_exists",
        "skills_dir_exists",
        "commands_dir_exists",
        "rules_dir_exists",
        "hooks_dir_exists",
        "python_tools_importable",
        "config_json_valid"
    ]
    for check in expected_checks:
        assert check in checks
