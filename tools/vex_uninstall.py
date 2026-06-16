import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

def print_json(data):
    print(json.dumps(data))

def cmd_uninstall(args):
    is_json = getattr(args, "json", False)
    auto_yes = getattr(args, "yes", False)
    
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        if is_json:
            print_json({"ok": False, "command": "uninstall", "error": "~/.claude not found"})
        else:
            print("Error: ~/.claude directory not found.")
        return 1

    if not auto_yes:
        if is_json:
            print_json({"ok": False, "command": "uninstall", "error": "Confirmation required (use --yes)"})
            return 1
        else:
            confirm = input(f"Are you sure you want to completely remove VEX from {claude_dir}? This will backup first. [y/N] ")
            if confirm.lower() != 'y':
                print("Uninstall cancelled.")
                return 0

    backup_dir = Path.home() / f".claude/vex-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # Create backup inside .claude since user data is there
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Move managed directories instead of full delete
        managed_dirs = ["agents", "skills", "commands", "rules", "hooks"]
        for d in managed_dirs:
            src = claude_dir / d
            if src.exists() and src.is_dir():
                shutil.copytree(src, backup_dir / d, dirs_exist_ok=True)
                shutil.rmtree(src)
                
        # Remove specific files
        managed_files = ["AGENTS.md"]
        for f in managed_files:
            src = claude_dir / f
            if src.exists():
                shutil.copy2(src, backup_dir / f)
                src.unlink()
                
        # Path cleanup (simplified for now, full .bashrc parsing is complex and risky)
        
        if is_json:
            print_json({
                "ok": True, 
                "command": "uninstall", 
                "data": {
                    "backed_up_to": str(backup_dir),
                    "removed": managed_dirs + managed_files
                }
            })
        else:
            print(f"✅ VEX uninstalled successfully. Backup saved to: {backup_dir}")
        return 0
    except Exception as e:
        if is_json:
            print_json({"ok": False, "command": "uninstall", "error": str(e)})
        else:
            print(f"Error during uninstall: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Uninstall VEX")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--yes", action="store_true", help="Automatic yes to prompts")
    args = parser.parse_args()
    sys.exit(cmd_uninstall(args))
