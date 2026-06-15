#!/usr/bin/env python3
"""VEX Skill Generator — Auto-generate skills from Claude Code session patterns.

Usage:
    python vex-skill-gen.py scan [--project NAME] [--min-occurrences N]
    python vex-skill-gen.py generate [--project NAME] [--output DIR]
    python vex-skill-gen.py install [--skill PATH] [--target DIR]
    python vex-skill-gen.py list [--score-min N]
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SESSIONS_ROOT = os.path.expanduser("~/.claude/projects")
SKILL_SCORE_MIN = 7


def find_session_files(project=None):
    """Find all JSONL session files under ~/.claude/projects/."""
    base = Path(SESSIONS_ROOT)
    if not base.exists():
        return []
    files = []
    for proj_dir in base.iterdir():
        if not proj_dir.is_dir():
            continue
        if project and proj_dir.name != project:
            continue
        sessions_dir = proj_dir / "sessions"
        if sessions_dir.is_dir():
            for f in sessions_dir.iterdir():
                if f.suffix == ".jsonl":
                    files.append((proj_dir.name, f))
    return files


def parse_session(filepath):
    """Parse a JSONL session log into structured entries."""
    entries = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry["_lineno"] = lineno
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    except (OSError, PermissionError):
        pass
    return entries


def extract_tool_calls(entries):
    """Extract tool calls and their patterns from session entries."""
    tool_calls = []
    for entry in entries:
        # Claude Code JSONL format: look for tool_use blocks
        msg_type = entry.get("type", "")
        
        # Handle assistant messages with content blocks
        if msg_type == "assistant" or entry.get("role") == "assistant":
            content = entry.get("message", entry)
            if isinstance(content, dict):
                blocks = content.get("content", [])
                if isinstance(blocks, str):
                    continue
                for block in blocks:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls.append({
                            "tool": block.get("name", "unknown"),
                            "input": block.get("input", {}),
                            "timestamp": entry.get("timestamp", ""),
                        })

        # Handle tool result entries
        if msg_type == "tool_result" or entry.get("type") == "tool_result":
            pass  # paired with tool_use

        # Alternative format: direct tool field
        if "tool" in entry and isinstance(entry["tool"], str):
            tool_calls.append({
                "tool": entry["tool"],
                "input": entry.get("input", entry.get("parameters", {})),
                "timestamp": entry.get("timestamp", ""),
            })

        # Handle content array with tool_use
        content = entry.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_calls.append({
                        "tool": block.get("name", "unknown"),
                        "input": block.get("input", {}),
                        "timestamp": entry.get("timestamp", ""),
                    })

    return tool_calls


def find_patterns(tool_calls, min_occurrences=2):
    """Detect recurring tool call patterns (sequences of 2-4 calls)."""
    tool_names = [tc["tool"] for tc in tool_calls]
    
    # N-gram patterns (bigrams, trigrams, 4-grams)
    patterns = Counter()
    for n in (2, 3, 4):
        for i in range(len(tool_names) - n + 1):
            seq = tuple(tool_names[i:i + n])
            patterns[seq] += 1

    # Filter by min occurrences
    significant = {k: v for k, v in patterns.items() if v >= min_occurrences}

    # Extract file-level patterns from inputs
    file_interactions = defaultdict(list)
    for tc in tool_calls:
        inp = tc["input"]
        if isinstance(inp, dict):
            # Try common file path keys
            for key in ("path", "file", "file_path", "filename", "filePath"):
                fp = inp.get(key)
                if fp and isinstance(fp, str):
                    file_interactions[fp].append(tc["tool"])
                    break

    return significant, file_interactions


def extract_topics(entries):
    """Extract topic/task descriptions from user messages."""
    topics = []
    for entry in entries:
        msg = entry.get("message", entry)
        role = msg.get("role", entry.get("role", ""))
        if role == "user":
            content = msg.get("content", entry.get("content", ""))
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        topics.append(block["text"][:200])
            elif isinstance(content, str) and content.strip():
                topics.append(content[:200])
    return topics


def score_skill(specificity, actionability, coverage, occurrence_count):
    """Score a skill from 0-10 based on quality metrics.
    
    specificity: 0-3 (how specific is the pattern)
    actionability: 0-3 (how useful for future tasks)
    coverage: 0-2 (how many sessions/projects covered)
    occurrence_count: 0-2 (frequency bonus)
    """
    score = 0.0
    
    # Specificity: unique tool combos score higher
    score += min(specificity, 3.0)
    
    # Actionability: patterns with clear workflows
    score += min(actionability, 3.0)
    
    # Coverage: multi-session patterns
    score += min(coverage, 2.0)
    
    # Frequency bonus
    if occurrence_count >= 5:
        score += 2.0
    elif occurrence_count >= 3:
        score += 1.0
    elif occurrence_count >= 2:
        score += 0.5

    return round(min(score, 10.0), 1)


def compute_quality(pattern_seq, occurrences, file_count, project_count):
    """Compute quality scores for a pattern."""
    # Specificity: unique tools in the pattern
    unique_tools = len(set(pattern_seq))
    specificity = unique_tools * 0.8  # 3+ unique tools = max

    # Actionability: patterns that include editing/writing/testing
    actionable_tools = {"write_file", "edit", "patch", "test", "run", "execute",
                        "Bash", "Write", "Edit", "MultiEdit", "create", "apply_patch"}
    has_action = any(t in actionable_tools for t in pattern_seq)
    actionability = 2.5 if has_action else 1.0

    # Coverage
    coverage = 0.0
    if project_count >= 2:
        coverage += 1.0
    if file_count >= 3:
        coverage += 1.0

    return score_skill(specificity, actionability, coverage, occurrences)


def generate_skill_md(name, pattern_seq, occurrences, files_involved, topics, score, project_name):
    """Generate SKILL.md content with frontmatter."""
    # Build description from topics
    desc_topics = topics[:5] if topics else ["code pattern"]
    summary = f"Auto-detected pattern: {' -> '.join(pattern_seq)} ({occurrences} occurrences)"

    # Category detection
    category = "general"
    tool_set = set(pattern_seq)
    if tool_set & {"grep", "search", "Grep", "Search"}:
        category = "search"
    if tool_set & {"edit", "write_file", "Write", "Edit", "MultiEdit", "apply_patch"}:
        category = "editing"
    if tool_set & {"test", "run", "Bash", "execute"}:
        category = "testing"

    frontmatter = f"""---
name: {name}
version: 1.0.0
category: {category}
score: {score}
auto_generated: true
source: vex-skill-gen
project: {project_name}
generated: {datetime.now().isoformat()}
---"""

    files_section = "\n".join(f"- `{f}`" for f in files_involved[:10])
    topics_section = "\n".join(f"- {t[:120]}" for t in topics[:5])

    content = f"""{frontmatter}

# {name}

{summary}

## Pattern

```
{' -> '.join(pattern_seq)}
```

- **Occurrences**: {occurrences}
- **Score**: {score}/10

## Files Involved

{files_section or '- (no files tracked)'}

## Source Topics

{topics_section or '- (no topics extracted)'}

## Instructions

When encountering similar tasks:

1. Follow the tool sequence: `{'` -> `'.join(pattern_seq)}`
2. Focus on the file types and patterns identified above.
3. Apply the same workflow structure for consistency.

## Notes

Auto-generated by VEX Skill Generator from Claude Code session analysis.
Review and refine this skill before relying on it in production workflows.
"""
    return content


def cmd_scan(args):
    """Scan sessions and display detected patterns."""
    session_files = find_session_files(args.project)
    if not session_files:
        print(f"No session files found at {SESSIONS_ROOT}")
        print("Run some Claude Code sessions first, then re-scan.")
        return

    print(f"Scanning {len(session_files)} session(s)...")
    all_patterns = Counter()
    all_files = defaultdict(set)
    all_topics = []
    project_counts = defaultdict(int)

    for proj_name, filepath in session_files:
        entries = parse_session(filepath)
        tool_calls = extract_tool_calls(entries)
        patterns, file_interactions = find_patterns(tool_calls, args.min_occurrences)
        topics = extract_topics(entries)
        all_topics.extend(topics)
        project_counts[proj_name] += 1

        for seq, count in patterns.items():
            all_patterns[seq] += count
        for fp, tools in file_interactions.items():
            all_files[fp].update(tools)

    if not all_patterns:
        print("No recurring patterns found.")
        print("Tip: use --min-occurrences 1 to see all patterns.")
        return

    print(f"\nFound {len(all_patterns)} pattern(s):\n")
    print(f"{'Pattern':<60} {'Count':>6} {'Tools':>5}")
    print("-" * 75)

    for seq, count in all_patterns.most_common(30):
        pattern_str = " -> ".join(seq)
        if len(pattern_str) > 58:
            pattern_str = pattern_str[:55] + "..."
        print(f"{pattern_str:<60} {count:>6} {len(seq):>5}")

    print(f"\nFiles involved: {len(all_files)}")
    print(f"Projects scanned: {len(project_counts)}")
    print(f"Topics extracted: {len(all_topics)}")


def cmd_generate(args):
    """Generate skills from detected patterns."""
    session_files = find_session_files(args.project)
    if not session_files:
        print(f"No session files found at {SESSIONS_ROOT}")
        return

    print(f"Analyzing {len(session_files)} session(s)...")

    all_patterns = Counter()
    all_files = defaultdict(set)
    all_topics = []
    project_counts = defaultdict(int)
    pattern_to_files = defaultdict(set)
    pattern_to_topics = defaultdict(list)

    for proj_name, filepath in session_files:
        entries = parse_session(filepath)
        tool_calls = extract_tool_calls(entries)
        patterns, file_interactions = find_patterns(tool_calls, max(args.min_occurrences, 1))
        topics = extract_topics(entries)
        all_topics.extend(topics)
        project_counts[proj_name] += 1

        for seq, count in patterns.items():
            all_patterns[seq] += count
            for topic in topics[:3]:
                pattern_to_topics[seq].append(topic)
        for fp, tools in file_interactions.items():
            all_files[fp].update(tools)
            for seq in patterns:
                pattern_to_files[seq].add(fp)

    output_dir = Path(args.output)
    generated = 0
    skipped = 0

    for seq, count in all_patterns.most_common():
        if count < args.min_occurrences:
            continue

        unique_tools = len(set(seq))
        files_involved = pattern_to_files.get(seq, set())
        topics_for_pattern = pattern_to_topics.get(seq, [])
        proj_count = len(set(p for p, _ in session_files))

        score = compute_quality(seq, count, len(files_involved), proj_count)

        if score < SKILL_SCORE_MIN:
            skipped += 1
            continue

        # Generate skill name
        tool_names = "-".join(seq).lower().replace("_", "-")
        name = f"auto-{tool_names}"

        # Project name for metadata
        proj_name = args.project or "multi-project"

        content = generate_skill_md(
            name, seq, count, list(files_involved), topics_for_pattern, score, proj_name
        )

        skill_dir = output_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text(content, encoding="utf-8")
        generated += 1
        print(f"  Generated: {name} (score: {score}, count: {count})")

    print(f"\nGenerated {generated} skill(s), skipped {skipped} below score {SKILL_SCORE_MIN}")
    if generated:
        print(f"Output: {output_dir}")


def cmd_install(args):
    """Install a generated skill to target directory."""
    skill_path = Path(args.skill)
    if not skill_path.exists():
        print(f"Skill not found: {skill_path}")
        return 1

    if skill_path.is_dir():
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            print(f"No SKILL.md found in {skill_path}")
            return 1
        skill_path = skill_md

    target = Path(args.target)
    skill_name = skill_path.parent.name if skill_path.name == "SKILL.md" else skill_path.stem
    install_dir = target / skill_name
    install_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    if skill_path.parent != install_dir:
        for f in skill_path.parent.iterdir():
            dest = install_dir / f.name
            shutil.copy2(f, dest)
            print(f"  Installed: {dest}")
    else:
        print(f"  Already at target: {install_dir}")

    print(f"\nSkill '{skill_name}' installed to {install_dir}")
    return 0


def cmd_list(args):
    """List installed auto-generated skills."""
    search_dirs = [
        Path.home() / ".claude" / "skills",
        Path("skills"),
    ]

    if args.search_dir:
        search_dirs.insert(0, Path(args.search_dir))

    found = []
    for sd in search_dirs:
        if not sd.exists():
            continue
        for skill_md in sd.rglob("SKILL.md"):
            # Read and check if auto-generated
            try:
                content = skill_md.read_text(encoding="utf-8", errors="replace")
                if "auto_generated: true" in content:
                    # Parse score
                    score_match = re.search(r"score:\s*([\d.]+)", content)
                    score = float(score_match.group(1)) if score_match else 0.0
                    name_match = re.search(r"name:\s*(.+)", content)
                    name = name_match.group(1).strip() if name_match else skill_md.parent.name
                    cat_match = re.search(r"category:\s*(\S+)", content)
                    category = cat_match.group(1) if cat_match else "unknown"
                    if score >= args.score_min:
                        found.append((name, score, category, skill_md.parent))
            except (OSError, PermissionError):
                continue

    if not found:
        print("No auto-generated skills found.")
        print(f"Searched: {', '.join(str(d) for d in search_dirs)}")
        return

    found.sort(key=lambda x: x[1], reverse=True)
    print(f"{'Name':<40} {'Score':>6} {'Category':<12} {'Path'}")
    print("-" * 90)
    for name, score, cat, path in found:
        print(f"{name:<40} {score:>6.1f} {cat:<12} {path}")


def main():
    parser = argparse.ArgumentParser(
        description="VEX Skill Generator — Auto-generate skills from Claude Code sessions"
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="Scan sessions for tool call patterns")
    p_scan.add_argument("--project", help="Filter by project name")
    p_scan.add_argument("--min-occurrences", type=int, default=2, help="Min pattern count (default: 2)")

    # generate
    p_gen = sub.add_parser("generate", help="Generate skill files from patterns")
    p_gen.add_argument("--project", help="Filter by project name")
    p_gen.add_argument("--output", default="./skills", help="Output directory (default: ./skills)")
    p_gen.add_argument("--min-occurrences", type=int, default=2, help="Min pattern count")

    # install
    p_inst = sub.add_parser("install", help="Install a skill to target directory")
    p_inst.add_argument("--skill", required=True, help="Skill path (file or directory)")
    p_inst.add_argument("--target", default="./skills", help="Target directory")

    # list
    p_list = sub.add_parser("list", help="List auto-generated skills")
    p_list.add_argument("--score-min", type=float, default=0, help="Min score filter")
    p_list.add_argument("--search-dir", help="Custom search directory")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "install":
        sys.exit(cmd_install(args))
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
