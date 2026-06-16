#!/usr/bin/env python3
"""VEX Skill Creator — Generate skills from git history patterns."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "generated-skill"


def git_oneline(days: int) -> list[tuple[str, str]]:
    output = run_git(["log", "--oneline", f'--since={days} days ago'])
    commits = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split(" ", 1)
        if len(parts) == 2:
            commits.append((parts[0], parts[1]))
    return commits


def git_commit_files(commit: str) -> list[str]:
    output = run_git(["diff", "--stat", f"{commit}^", commit])
    files = []
    for line in output.splitlines():
        if "|" not in line:
            continue
        name = line.split("|", 1)[0].strip()
        if name:
            files.append(name)
    return files


def git_commit_bodies(days: int) -> list[str]:
    output = run_git(["log", "--format=%s%n%b%x1e", f'--since={days} days ago'])
    return [part.strip() for part in output.split("\x1e") if part.strip()]


def extract_commands(messages: list[str]) -> Counter[str]:
    commands: Counter[str] = Counter()
    patterns = [
        r"`([^`]+)`",
        r"(?:run|use|execute)\s+([a-zA-Z0-9_./:-]+(?:\s+[a-zA-Z0-9_./:=:-]+){0,4})",
    ]
    for message in messages:
        for pattern in patterns:
            for match in re.findall(pattern, message, flags=re.IGNORECASE):
                command = " ".join(str(match).strip().split())
                if command and re.search(r"\b(pytest|python|npm|git|vex|ruff|mypy|node|bash)\b", command):
                    commands[command] += 1
    return commands


def extract_fix_patterns(messages: list[str]) -> Counter[str]:
    fixes: Counter[str] = Counter()
    for message in messages:
        first_line = message.splitlines()[0].strip()
        normalized = re.sub(r"^[a-z]+(?:\([^)]*\))?!?:\s*", "", first_line, flags=re.IGNORECASE)
        normalized = re.sub(r"\s+", " ", normalized)
        if re.search(r"\b(fix|repair|correct|match|guard|validate|handle|prevent)\b", first_line, re.IGNORECASE):
            fixes[normalized[:120]] += 1
    return fixes


def extract_cochanges(commits: list[tuple[str, str]]) -> Counter[tuple[str, str]]:
    pairs: Counter[tuple[str, str]] = Counter()
    for commit, _ in commits:
        try:
            files = sorted(set(git_commit_files(commit)))
        except RuntimeError:
            continue
        for left_index, left in enumerate(files):
            for right in files[left_index + 1 :]:
                pairs[(left, right)] += 1
    return pairs


def summarize_areas(cochanges: Counter[tuple[str, str]]) -> Counter[str]:
    areas: Counter[str] = Counter()
    for pair, count in cochanges.items():
        for file_name in pair:
            area = file_name.split("/", 1)[0]
            areas[area] += count
    return areas


def yaml_escape(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def bullet_list(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}\n"
    return "".join(f"- {item}\n" for item in items)


def build_skill(name: str, days: int, commits: list[tuple[str, str]], cochanges: Counter[tuple[str, str]], commands: Counter[str], fixes: Counter[str]) -> str:
    areas = summarize_areas(cochanges)
    top_areas = [f"`{area}/` changed repeatedly" for area, _ in areas.most_common(5)]
    top_pairs = [f"`{left}` with `{right}` ({count} commits)" for (left, right), count in cochanges.most_common(8)]
    top_commands = [f"Run `{command}` when pattern fits ({count} mentions)" for command, count in commands.most_common(8)]
    top_fixes = [f"{pattern} ({count} commits)" for pattern, count in fixes.most_common(8)]

    description = f"Generated from {len(commits)} commits over last {days} days."
    return (
        "---\n"
        f"name: {yaml_escape(name)}\n"
        f"description: {yaml_escape(description)}\n"
        "metadata:\n"
        "  type: generated-skill\n"
        "  source: git-history\n"
        f"  days: {days}\n"
        "---\n\n"
        f"# {name}\n\n"
        "## When to Activate\n\n"
        + bullet_list(top_areas, "Use when recent git history suggests repeated maintenance in same project area.")
        + "\n## How It Works\n\n"
        + bullet_list(
            [
                "Review recent commits for files that tend to change together.",
                "Reuse repeated commands from commit messages when validating similar work.",
                "Prefer fixes matching repeated historical failure modes.",
            ],
            "Analyze git history, then apply repeated patterns.",
        )
        + "\n## Common Patterns\n\n"
        + "### Co-change Patterns\n\n"
        + bullet_list(top_pairs, "No strong co-change pattern found.")
        + "\n### Recurring Commands\n\n"
        + bullet_list(top_commands, "No recurring command found in commit messages.")
        + "\n### Fix Patterns\n\n"
        + bullet_list(top_fixes, "No recurring fix pattern found.")
    )


def write_skill(output: Path, name: str, content: str) -> Path:
    skill_dir = output / slug(name)
    skill_dir.mkdir(parents=True, exist_ok=True)
    target = skill_dir / "SKILL.md"
    target.write_text(content, encoding="utf-8")
    return target


def analyze(days: int) -> dict[str, object]:
    commits = git_oneline(days)
    messages = git_commit_bodies(days)
    cochanges = extract_cochanges(commits)
    commands = extract_commands(messages)
    fixes = extract_fix_patterns(messages)
    return {
        "commits": commits,
        "cochanges": cochanges,
        "commands": commands,
        "fixes": fixes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate VEX skills from git history patterns")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", default="skills/")
    parser.add_argument("--name", default="git-history-skill")
    args = parser.parse_args()

    if args.days < 1:
        parser.error("--days must be >= 1")

    result = analyze(args.days)
    content = build_skill(
        args.name,
        args.days,
        result["commits"],
        result["cochanges"],
        result["commands"],
        result["fixes"],
    )
    target = write_skill((REPO_ROOT / args.output).resolve(), args.name, content)
    print(json.dumps({"ok": True, "skill": str(target), "commits": len(result["commits"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
