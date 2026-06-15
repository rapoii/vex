#!/usr/bin/env python3
"""VEX Memory — Cross-project knowledge graph for Claude Code sessions.

Usage:
    python vex-memory.py scan [--project NAME] [--rebuild]
    python vex-memory.py search QUERY [--type file|pattern|solution] [--limit N]
    python vex-memory.py context [--file PATH] [--project NAME]
    python vex-memory.py export [--format json|dot] [--output FILE]
    python vex-memory.py stats
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
GRAPH_FILE = os.path.expanduser("~/.vex/knowledge_graph.json")


def ensure_vex_dir():
    d = Path.home() / ".vex"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_graph():
    try:
        with open(GRAPH_FILE, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "version": 2,
            "last_scan": None,
            "projects": {},
            "files": {},
            "patterns": {},
            "solutions": {},
            "edges": [],
        }


def save_graph(graph):
    ensure_vex_dir()
    graph["last_scan"] = datetime.now().isoformat()
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


def find_session_files(project=None):
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
    entries = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (OSError, PermissionError):
        pass
    return entries


def extract_files_mentioned(entries):
    """Extract file paths mentioned in tool calls and messages."""
    files = Counter()
    # Common file path patterns
    path_pattern = re.compile(
        r'(?:^|[\s`"\'])([^\s`"\']*?(?:'
        r'(?:src|lib|app|test|tests|spec|specs|cmd|pkg|internal|vendor|'
        r'components|pages|api|utils|services|models|routes|middleware|'
        r'config|scripts|tools|docs|build|dist|public|static|assets)'
        r'/[^\s`"\']*\.[a-zA-Z0-9]{1,10})'
        r')',
        re.MULTILINE,
    )

    for entry in entries:
        content_str = ""

        # Extract from various content locations
        msg = entry.get("message", entry)
        if isinstance(msg, dict):
            blocks = msg.get("content", [])
            if isinstance(blocks, str):
                content_str = blocks
            elif isinstance(blocks, list):
                for block in blocks:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_use":
                            inp = block.get("input", {})
                            if isinstance(inp, dict):
                                for key in ("path", "file_path", "file", "filename", "filePath", "command"):
                                    val = inp.get(key, "")
                                    if isinstance(val, str) and "." in val:
                                        # Extract file paths from commands too
                                        for m in path_pattern.finditer(val):
                                            files[m.group(1)] += 1
                                        if "/" in val or "\\" in val:
                                            files[val.strip()] += 1
                        elif block.get("type") == "text":
                            content_str += " " + block.get("text", "")
                    elif isinstance(block, str):
                        content_str += " " + block

        # Also check direct content
        direct = entry.get("content", "")
        if isinstance(direct, str):
            content_str += " " + direct

        # Search for file paths in content
        for m in path_pattern.finditer(content_str):
            files[m.group(1)] += 1

    return files


def extract_solutions(entries):
    """Extract solution patterns (tool sequences that produced results)."""
    solutions = []
    current_sequence = []
    
    for entry in entries:
        msg = entry.get("message", entry)
        role = ""
        if isinstance(msg, dict):
            role = msg.get("role", entry.get("role", ""))

        if role in ("assistant", ""):
            blocks = msg.get("content", []) if isinstance(msg, dict) else []
            if isinstance(blocks, str):
                continue
            for block in blocks:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_name = block.get("name", "unknown")
                    inp = block.get("input", {})
                    current_sequence.append({
                        "tool": tool_name,
                        "summary": _summarize_tool_input(tool_name, inp),
                    })

        # After tool results, consider sequence complete
        if role == "user" and current_sequence:
            if len(current_sequence) >= 2:
                solutions.append(list(current_sequence))
            current_sequence = []

    # Final sequence
    if len(current_sequence) >= 2:
        solutions.append(current_sequence)

    return solutions


def _summarize_tool_input(tool_name, inp):
    """Create short summary of a tool call."""
    if not isinstance(inp, dict):
        return str(inp)[:80]
    
    path = inp.get("path", inp.get("file", inp.get("file_path", "")))
    command = inp.get("command", "")
    query = inp.get("query", inp.get("pattern", inp.get("regex", "")))

    if path:
        return f"{tool_name}({path})"
    if command:
        cmd_short = command[:60].split("\n")[0]
        return f"{tool_name}({cmd_short})"
    if query:
        return f"{tool_name}({query})"
    return tool_name


def extract_patterns(entries):
    """Extract recurring code patterns and conventions."""
    patterns = {}
    
    # Look for error/fix patterns
    for entry in entries:
        msg = entry.get("message", entry)
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", entry.get("role", ""))
        if role != "user":
            continue
        
        content = msg.get("content", "")
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block["text"])
            content = " ".join(text_parts)

        if not isinstance(content, str):
            continue

        # Error patterns
        errors = re.findall(r'(?:error|Error|ERROR)[:\s]+(.{10,100})', content)
        for err in errors:
            key = err.strip()[:60]
            patterns.setdefault(key, {"type": "error", "count": 0, "examples": []})
            patterns[key]["count"] += 1
            if len(patterns[key]["examples"]) < 3:
                patterns[key]["examples"].append(err.strip()[:100])

    return patterns


def cmd_scan(args):
    """Scan sessions and build knowledge graph."""
    graph = load_graph() if not args.rebuild else {
        "version": 2, "last_scan": None,
        "projects": {}, "files": {}, "patterns": {},
        "solutions": {}, "edges": [],
    }

    session_files = find_session_files(args.project)
    if not session_files:
        print(f"No session files found at {SESSIONS_ROOT}")
        return

    print(f"Scanning {len(session_files)} session(s)...")

    edge_set = set(tuple(e) for e in graph.get("edges", []))
    new_projects = 0
    new_files = 0
    new_patterns = 0
    new_solutions = 0

    for proj_name, filepath in session_files:
        entries = parse_session(filepath)
        if not entries:
            continue

        # Register project
        if proj_name not in graph["projects"]:
            graph["projects"][proj_name] = {
                "name": proj_name,
                "session_count": 0,
                "file_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
            }
            new_projects += 1
        graph["projects"][proj_name]["session_count"] += 1
        graph["projects"][proj_name]["last_seen"] = datetime.now().isoformat()

        # Extract files
        mentioned_files = extract_files_mentioned(entries)
        for fp, count in mentioned_files.items():
            if fp not in graph["files"]:
                graph["files"][fp] = {
                    "path": fp,
                    "projects": [],
                    "access_count": 0,
                    "first_seen": datetime.now().isoformat(),
                }
                new_files += 1
            graph["files"][fp]["access_count"] += count
            if proj_name not in graph["files"][fp]["projects"]:
                graph["files"][fp]["projects"].append(proj_name)
                graph["projects"][proj_name]["file_count"] += 1

            # Edge: project -> file
            edge = ("project", proj_name, "file", fp)
            if edge not in edge_set:
                edge_set.add(edge)

        # Extract patterns
        patterns = extract_patterns(entries)
        for pat_key, pat_data in patterns.items():
            if pat_key not in graph["patterns"]:
                graph["patterns"][pat_key] = {
                    "key": pat_key,
                    "type": pat_data["type"],
                    "count": 0,
                    "examples": [],
                    "projects": [],
                }
                new_patterns += 1
            graph["patterns"][pat_key]["count"] += pat_data["count"]
            graph["patterns"][pat_key]["examples"] = pat_data["examples"]
            if proj_name not in graph["patterns"][pat_key]["projects"]:
                graph["patterns"][pat_key]["projects"].append(proj_name)

            edge = ("project", proj_name, "pattern", pat_key)
            if edge not in edge_set:
                edge_set.add(edge)

        # Extract solutions
        solutions = extract_solutions(entries)
        for sol in solutions:
            sol_key = " -> ".join(s["tool"] for s in sol)
            if sol_key not in graph["solutions"]:
                graph["solutions"][sol_key] = {
                    "sequence": [s["summary"] for s in sol],
                    "tools": [s["tool"] for s in sol],
                    "count": 0,
                    "projects": [],
                }
                new_solutions += 1
            graph["solutions"][sol_key]["count"] += 1
            if proj_name not in graph["solutions"][sol_key]["projects"]:
                graph["solutions"][sol_key]["projects"].append(proj_name)

            # Edge: file -> solution (for files in the sequence)
            for s in sol:
                if "(" in s["summary"]:
                    involved_file = s["summary"].split("(", 1)[1].rstrip(")")
                    edge = ("file", involved_file, "solution", sol_key)
                    if edge not in edge_set:
                        edge_set.add(edge)

    graph["edges"] = [list(e) for e in edge_set]
    save_graph(graph)

    print(f"\nKnowledge graph updated:")
    print(f"  Projects:  {len(graph['projects'])} (+{new_projects})")
    print(f"  Files:     {len(graph['files'])} (+{new_files})")
    print(f"  Patterns:  {len(graph['patterns'])} (+{new_patterns})")
    print(f"  Solutions: {len(graph['solutions'])} (+{new_solutions})")
    print(f"  Edges:     {len(graph['edges'])}")
    print(f"\nGraph saved to: {GRAPH_FILE}")


def cmd_search(args):
    """Search the knowledge graph."""
    graph = load_graph()
    query = args.query.lower()
    limit = args.limit

    results = []

    if args.type in (None, "file"):
        for fp, fdata in graph["files"].items():
            if query in fp.lower():
                results.append(("file", fp, fdata))

    if args.type in (None, "pattern"):
        for pk, pdata in graph["patterns"].items():
            if query in pk.lower() or any(query in e.lower() for e in pdata.get("examples", [])):
                results.append(("pattern", pk, pdata))

    if args.type in (None, "solution"):
        for sk, sdata in graph["solutions"].items():
            if query in sk.lower() or any(query in s.lower() for s in sdata.get("sequence", [])):
                results.append(("solution", sk, sdata))

    if not results:
        print(f"No results for '{args.query}'")
        return

    print(f"Found {len(results)} result(s) for '{args.query}':\n")

    for kind, key, data in results[:limit]:
        print(f"[{kind.upper()}] {key}")
        if kind == "file":
            print(f"  Access count: {data['access_count']}")
            print(f"  Projects: {', '.join(data['projects'])}")
        elif kind == "pattern":
            print(f"  Count: {data['count']}")
            print(f"  Projects: {', '.join(data['projects'])}")
            for ex in data.get("examples", [])[:2]:
                print(f"  Example: {ex}")
        elif kind == "solution":
            print(f"  Count: {data['count']}")
            print(f"  Projects: {', '.join(data['projects'])}")
            print(f"  Sequence: {' -> '.join(data['sequence'][:5])}")
        print()


def cmd_context(args):
    """Show context for a file or project — related files, patterns, solutions."""
    graph = load_graph()

    if args.file:
        fp = args.file
        print(f"\nContext for: {fp}\n")

        # Find related files (files in same projects)
        file_data = graph["files"].get(fp, {})
        if not file_data:
            # Fuzzy match
            matches = [k for k in graph["files"] if fp in k or k in fp]
            if matches:
                fp = matches[0]
                file_data = graph["files"][fp]
                print(f"  (matched to: {fp})")
            else:
                print(f"  File not found in graph.")
                return

        projects = file_data.get("projects", [])
        print(f"  Projects: {', '.join(projects)}")
        print(f"  Access count: {file_data.get('access_count', 0)}")

        # Related files (same project)
        related = set()
        for proj in projects:
            for other_fp, other_data in graph["files"].items():
                if other_fp != fp and proj in other_data.get("projects", []):
                    related.add(other_fp)
        if related:
            print(f"\n  Related files ({len(related)}):")
            for rf in sorted(related)[:10]:
                print(f"    - {rf}")

        # Solutions involving this file
        solutions = []
        for sk, sdata in graph["solutions"].items():
            if fp in sk or fp in str(sdata.get("sequence", [])):
                solutions.append((sk, sdata))
        if solutions:
            print(f"\n  Solutions ({len(solutions)}):")
            for sk, sd in solutions[:5]:
                print(f"    - {sk} (count: {sd['count']})")

        # Patterns from same projects
        proj_patterns = []
        for pk, pdata in graph["patterns"].items():
            if any(p in pdata.get("projects", []) for p in projects):
                proj_patterns.append((pk, pdata))
        if proj_patterns:
            print(f"\n  Project patterns ({len(proj_patterns)}):")
            proj_patterns.sort(key=lambda x: x[1]["count"], reverse=True)
            for pk, pd in proj_patterns[:5]:
                print(f"    - {pk} (count: {pd['count']})")

    elif args.project:
        proj = args.project
        print(f"\nContext for project: {proj}\n")

        pdata = graph["projects"].get(proj, {})
        if not pdata:
            print(f"  Project not found.")
            return

        print(f"  Sessions: {pdata.get('session_count', 0)}")
        print(f"  Files: {pdata.get('file_count', 0)}")
        print(f"  First seen: {pdata.get('first_seen', 'unknown')}")
        print(f"  Last seen: {pdata.get('last_seen', 'unknown')}")

        # Project files
        proj_files = [fp for fp, fd in graph["files"].items()
                      if proj in fd.get("projects", [])]
        if proj_files:
            print(f"\n  Files ({len(proj_files)}):")
            proj_files.sort(key=lambda f: graph["files"][f].get("access_count", 0), reverse=True)
            for f in proj_files[:15]:
                print(f"    - {f} ({graph['files'][f].get('access_count', 0)} accesses)")

        # Cross-project solutions
        cross_proj = []
        for sk, sdata in graph["solutions"].items():
            if proj in sdata.get("projects", []) and len(sdata.get("projects", [])) > 1:
                other_projects = [p for p in sdata["projects"] if p != proj]
                cross_proj.append((sk, sdata, other_projects))
        if cross_proj:
            print(f"\n  Cross-project solutions ({len(cross_proj)}):")
            for sk, sd, others in cross_proj[:5]:
                print(f"    - {sk} (also in: {', '.join(others)})")
    else:
        print("Specify --file or --project")


def cmd_export(args):
    """Export knowledge graph."""
    graph = load_graph()

    if args.format == "dot":
        lines = ["digraph VEXMemory {", '  rankdir=LR;', '  node [shape=box];', ""]

        # Project nodes
        for pname in graph["projects"]:
            lines.append(f'  "p_{pname}" [label="{pname}" style=filled fillcolor=lightblue];')

        # File nodes
        for fp in list(graph["files"])[:50]:
            safe = fp.replace("/", "_").replace(".", "_").replace("-", "_")
            short = fp.split("/")[-1] if "/" in fp else fp
            lines.append(f'  "f_{safe}" [label="{short}" style=filled fillcolor=lightyellow];')

        # Solution nodes
        for sk in list(graph["solutions"])[:30]:
            safe = sk.replace("->", "_").replace(" ", "")
            lines.append(f'  "s_{safe}" [label="{sk}" style=filled fillcolor=lightgreen];')

        lines.append("")

        # Edges
        for edge in graph.get("edges", [])[:200]:
            if len(edge) >= 4:
                src_type, src_key, dst_type, dst_key = edge[0], edge[1], edge[2], edge[3]
                src_prefix = src_type[0]
                dst_prefix = dst_type[0]
                src_safe = src_key.replace("/", "_").replace(".", "_").replace("-", "_")
                dst_safe = dst_key.replace("/", "_").replace(".", "_").replace("-", "_").replace("->", "_").replace(" ", "")
                lines.append(f'  "{src_prefix}_{src_safe}" -> "{dst_prefix}_{dst_safe}";')

        lines.append("}")
        content = "\n".join(lines)
    else:
        content = json.dumps(graph, indent=2)

    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Exported to {args.output}")
    else:
        print(content)


def cmd_stats(args):
    """Show knowledge graph statistics."""
    graph = load_graph()

    print(f"\n{'='*50}")
    print(f"  VEX Knowledge Graph Statistics")
    print(f"{'='*50}\n")

    print(f"Last scan: {graph.get('last_scan', 'never')}")
    print(f"Projects:  {len(graph.get('projects', {}))}")
    print(f"Files:     {len(graph.get('files', {}))}")
    print(f"Patterns:  {len(graph.get('patterns', {}))}")
    print(f"Solutions: {len(graph.get('solutions', {}))}")
    print(f"Edges:     {len(graph.get('edges', []))}")

    # Top projects by session count
    projects = graph.get("projects", {})
    if projects:
        print(f"\nTop projects by sessions:")
        sorted_proj = sorted(projects.items(), key=lambda x: x[1].get("session_count", 0), reverse=True)
        for name, data in sorted_proj[:10]:
            sc = data.get("session_count", 0)
            fc = data.get("file_count", 0)
            print(f"  {name:<30} {sc} sessions, {fc} files")

    # Top files
    files = graph.get("files", {})
    if files:
        print(f"\nMost accessed files:")
        sorted_files = sorted(files.items(), key=lambda x: x[1].get("access_count", 0), reverse=True)
        for fp, data in sorted_files[:10]:
            ac = data.get("access_count", 0)
            projs = len(data.get("projects", []))
            print(f"  {fp:<50} {ac:>5} accesses, {projs} project(s)")

    # Top patterns
    patterns = graph.get("patterns", {})
    if patterns:
        print(f"\nTop error patterns:")
        sorted_pats = sorted(patterns.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        for pk, data in sorted_pats[:10]:
            print(f"  {pk[:50]:<50} {data['count']} occurrences")

    # Top solutions
    solutions = graph.get("solutions", {})
    if solutions:
        print(f"\nTop solution sequences:")
        sorted_sols = sorted(solutions.items(), key=lambda x: x[1].get("count", 0), reverse=True)
        for sk, data in sorted_sols[:10]:
            projs = len(data.get("projects", []))
            print(f"  {sk:<50} {data['count']}x, {projs} project(s)")

    # Cross-project insights
    cross_solutions = {sk: sd for sk, sd in solutions.items()
                       if len(sd.get("projects", [])) > 1}
    if cross_solutions:
        print(f"\nCross-project solutions: {len(cross_solutions)}")
        for sk, sd in sorted(cross_solutions.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
            print(f"  {sk} -> {', '.join(sd['projects'])}")

    # Graph density
    n_nodes = len(projects) + len(files) + len(patterns) + len(solutions)
    n_edges = len(graph.get("edges", []))
    if n_nodes > 1:
        density = n_edges / (n_nodes * (n_nodes - 1))
        print(f"\nGraph density: {density:.6f}")
    print(f"Total nodes: {n_nodes}")


def main():
    parser = argparse.ArgumentParser(
        description="VEX Memory — Cross-project knowledge graph"
    )
    sub = parser.add_subparsers(dest="command")

    # scan
    p_scan = sub.add_parser("scan", help="Scan sessions and build knowledge graph")
    p_scan.add_argument("--project", help="Filter by project name")
    p_scan.add_argument("--rebuild", action="store_true", help="Rebuild graph from scratch")

    # search
    p_search = sub.add_parser("search", help="Search the knowledge graph")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--type", choices=["file", "pattern", "solution"], help="Filter by type")
    p_search.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")

    # context
    p_ctx = sub.add_parser("context", help="Show context for file or project")
    p_ctx.add_argument("--file", help="File path to get context for")
    p_ctx.add_argument("--project", help="Project name to get context for")

    # export
    p_export = sub.add_parser("export", help="Export knowledge graph")
    p_export.add_argument("--format", choices=["json", "dot"], default="json", help="Export format")
    p_export.add_argument("--output", help="Output file path")

    # stats
    sub.add_parser("stats", help="Show graph statistics")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "context":
        cmd_context(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
