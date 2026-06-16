import json
import pytest
import subprocess
from pathlib import Path

VEX_CLI = Path(__file__).parent.parent / "tools" / "vex.py"

def run_vex(*args):
    return subprocess.run(["python", str(VEX_CLI), *args], capture_output=True, text=True)

def test_repair_command():
    result = run_vex("repair", "--json")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["command"] == "repair"
    assert "fixed" in data["data"]
