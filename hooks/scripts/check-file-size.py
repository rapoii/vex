import json
import sys

payload = json.load(sys.stdin)
content = payload.get("tool_input", {}).get("content", "")
path = payload.get("tool_input", {}).get("file_path", "")
if path.endswith((".md", ".py", ".ts", ".tsx", ".js", ".jsx")) and content.count("\n") + 1 > 800:
    print(f"[VEX] BLOCKED: {path} exceeds 800 lines", file=sys.stderr)
    sys.exit(2)
print(json.dumps(payload))
