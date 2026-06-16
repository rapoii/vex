import argparse
import json
import os
import shutil
import stat
import sys
from pathlib import Path

def print_json(data):
    print(json.dumps(data))

def cmd_repair(args):
    is_json = getattr(args, "json", False)
    
    repo_root = Path(__file__).parent.parent.resolve()
    claude_dir = Path.home() / ".claude"
    
    fixed = []
    
    try:
        # Restore missing directories
        dirs_to_check = ["agents", "skills", "commands", "rules", "hooks"]
        for d in dirs_to_check:
            dest = claude_dir / d
            src = repo_root / d
            if not dest.exists() and src.exists():
                shutil.copytree(src, dest)
                fixed.append(f"Restored {d}/ directory")
                
        # Restore missing files
        files_to_check = ["AGENTS.md"]
        for f in files_to_check:
            dest = claude_dir / f
            src = repo_root / f
            if not dest.exists() and src.exists():
                shutil.copy2(src, dest)
                fixed.append(f"Restored {f}")
                
        # Fix script permissions
        scripts_dir = repo_root / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.glob("*.sh"):
                st = os.stat(script)
                os.chmod(script, st.st_mode | stat.S_IEXEC)
                fixed.append(f"Fixed permissions for {script.name}")
                
        if is_json:
            print_json({
                "ok": True,
                "command": "repair",
                "data": {"fixed": fixed}
            })
        else:
            print(f"✅ VEX Repair complete. Fixed {len(fixed)} issues.")
            for f in fixed:
                print(f"  - {f}")
        return 0
    except Exception as e:
        if is_json:
            print_json({"ok": False, "command": "repair", "error": str(e)})
        else:
            print(f"Error during repair: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair VEX installation")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.exit(cmd_repair(args))
