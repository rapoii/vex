import json
import pytest
import subprocess
from pathlib import Path

VEX_CLI = Path(__file__).parent.parent / "tools" / "vex.py"

def run_vex(*args):
    return subprocess.run(["python", str(VEX_CLI), *args], capture_output=True, text=True)

def test_uninstall_command_json():
    # Since uninstall needs confirmation, we simulate `--yes` or test the JSON output logic
    result = run_vex("uninstall", "--json", "--yes")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert data["command"] == "uninstall"
    assert "backed_up_to" in data["data"]
