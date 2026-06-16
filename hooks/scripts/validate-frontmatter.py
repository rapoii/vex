import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("name", "description")


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def target_path(payload: dict) -> Path | None:
    path = payload.get("tool_input", {}).get("file_path", "")
    if not isinstance(path, str) or not path:
        return None
    return Path(path)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    metadata: dict[str, str] = {}
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("'\"")

    return metadata if closed else None


def main() -> int:
    payload = read_payload()
    path = target_path(payload)
    if path is None or path.suffix != ".md" or not path.exists():
        return 0

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"[VEX] Cannot read markdown file: {path}: {error}", file=sys.stderr)
        return 1

    metadata = parse_frontmatter(text)
    if metadata is None:
        print(f"[VEX] Invalid YAML frontmatter: {path}", file=sys.stderr)
        return 1

    missing = [field for field in REQUIRED_FIELDS if not metadata.get(field)]
    if missing:
        print(f"[VEX] Missing frontmatter fields in {path}: {', '.join(missing)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
