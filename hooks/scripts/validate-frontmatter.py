import json
import pathlib
import re
import sys

payload = json.load(sys.stdin)
path = pathlib.Path(payload.get("tool_input", {}).get("file_path", ""))
if path.suffix != ".md" or not path.exists():
    sys.exit(0)
text = path.read_text(encoding="utf-8")
if not text.startswith("---\n"):
    print(f"[VEX] Missing YAML frontmatter: {path}", file=sys.stderr)
    sys.exit(2)
if not re.search(r"\n---\n", text[4:]):
    print(f"[VEX] Unterminated YAML frontmatter: {path}", file=sys.stderr)
    sys.exit(2)
