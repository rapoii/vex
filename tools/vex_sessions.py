"""Record and query Claude Code sessions in SQLite."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


DEFAULT_DB_NAME = "vex-sessions.db"


def vex_home() -> Path:
    return Path(os.environ.get("VEX_HOME", Path.home() / ".claude")).expanduser()


def db_path() -> Path:
    return vex_home() / DEFAULT_DB_NAME


def json_envelope(ok: bool, command: str, data: Any = None, error: dict[str, str] | None = None) -> dict[str, Any]:
    return {"ok": ok, "command": command, "data": data, "error": error}


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, sort_keys=True))


def hash_value(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, default=str) if not isinstance(value, str) else value
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def init_db(path: Path | None = None) -> Path:
    target = path or db_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(target)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start TEXT,
                end TEXT,
                project TEXT,
                model TEXT,
                cost REAL DEFAULT 0,
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT,
                type TEXT,
                tool TEXT,
                input_hash TEXT,
                output_hash TEXT,
                success INTEGER,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files_changed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                path TEXT,
                action TEXT,
                UNIQUE(session_id, path, action),
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
            """
        )
        conn.commit()
    return target


def session_log_dir() -> Path:
    return Path(os.environ.get("VEX_SESSION_DIR", Path.home() / ".claude" / "projects")).expanduser()


def iter_jsonl_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("*.jsonl"))


def parse_session_file(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]], int]:
    session_id = path.stem
    session = {"id": session_id, "start": None, "end": None, "project": None, "model": None, "cost": 0.0, "tokens_in": 0, "tokens_out": 0}
    events: list[dict[str, Any]] = []
    files: list[dict[str, str]] = []
    malformed = 0

    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw_line.strip():
            continue
        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError:
            malformed += 1
            continue

        current_id = str(item.get("session_id") or item.get("sessionId") or session_id)
        session["id"] = current_id
        timestamp = item.get("timestamp") or item.get("created_at") or item.get("time")
        item_type = item.get("type") or item.get("event") or "event"

        if item_type in {"session_start", "start"} and timestamp:
            session["start"] = session["start"] or timestamp
        elif item_type in {"session_end", "end"} and timestamp:
            session["end"] = timestamp
        elif timestamp and not session["start"]:
            session["start"] = timestamp

        session["project"] = session["project"] or item.get("project") or item.get("cwd")
        session["model"] = session["model"] or item.get("model")
        session["tokens_in"] += int(item.get("input_tokens") or item.get("tokens_in") or 0)
        session["tokens_out"] += int(item.get("output_tokens") or item.get("tokens_out") or 0)
        session["cost"] += float(item.get("cost_usd") or item.get("cost") or 0)

        tool = item.get("tool") or item.get("name") if item_type == "tool_call" else item.get("tool")
        events.append(
            {
                "session_id": current_id,
                "timestamp": timestamp,
                "type": item_type,
                "tool": tool,
                "input_hash": hash_value(item.get("input", "")),
                "output_hash": hash_value(item.get("output", "")),
                "success": 0 if item.get("success") is False else 1,
            }
        )

        file_path = item.get("path") or (item.get("input") or {}).get("file_path") if isinstance(item.get("input"), dict) else item.get("path")
        if item_type == "file_change" and file_path:
            files.append({"session_id": current_id, "path": str(file_path), "action": str(item.get("action") or "change")})
        elif tool in {"Write", "Edit", "MultiEdit"} and file_path:
            files.append({"session_id": current_id, "path": str(file_path), "action": tool.lower()})

    return session, events, files, malformed


def record_sessions(root: Path) -> dict[str, int]:
    database = init_db()
    totals = {"sessions": 0, "events": 0, "files_changed": 0, "malformed_lines": 0}
    with sqlite3.connect(database) as conn:
        for path in iter_jsonl_files(root):
            session, events, files, malformed = parse_session_file(path)
            conn.execute(
                """
                INSERT INTO sessions (id, start, end, project, model, cost, tokens_in, tokens_out)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    start=excluded.start,
                    end=excluded.end,
                    project=excluded.project,
                    model=excluded.model,
                    cost=excluded.cost,
                    tokens_in=excluded.tokens_in,
                    tokens_out=excluded.tokens_out
                """,
                (session["id"], session["start"], session["end"], session["project"], session["model"], session["cost"], session["tokens_in"], session["tokens_out"]),
            )
            conn.execute("DELETE FROM events WHERE session_id = ?", (session["id"],))
            conn.executemany(
                "INSERT INTO events (session_id, timestamp, type, tool, input_hash, output_hash, success) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [(event["session_id"], event["timestamp"], event["type"], event["tool"], event["input_hash"], event["output_hash"], event["success"]) for event in events],
            )
            conn.executemany(
                "INSERT OR IGNORE INTO files_changed (session_id, path, action) VALUES (?, ?, ?)",
                [(file["session_id"], file["path"], file["action"]) for file in files],
            )
            totals["sessions"] += 1
            totals["events"] += len(events)
            totals["files_changed"] += len(files)
            totals["malformed_lines"] += malformed
    return totals


def parse_since(value: str | None) -> str | None:
    if not value:
        return None
    if value.endswith("d") and value[:-1].isdigit():
        cutoff = datetime.now(timezone.utc) - timedelta(days=int(value[:-1]))
        return cutoff.isoformat()
    return value


def list_sessions(project: str | None, since: str | None) -> list[dict[str, Any]]:
    init_db()
    where = []
    params: list[Any] = []
    if project:
        where.append("project = ?")
        params.append(project)
    cutoff = parse_since(since)
    if cutoff:
        where.append("start >= ?")
        params.append(cutoff)
    query = "SELECT id, start, end, project, model, cost, tokens_in, tokens_out FROM sessions"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY COALESCE(start, '') DESC"
    with sqlite3.connect(db_path()) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(query, params)]


def stats() -> dict[str, Any]:
    init_db()
    with sqlite3.connect(db_path()) as conn:
        row = conn.execute("SELECT COUNT(*), COALESCE(SUM(cost), 0), COALESCE(SUM(tokens_in), 0), COALESCE(SUM(tokens_out), 0) FROM sessions").fetchone()
        events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    return {"sessions": row[0], "cost": row[1], "tokens_in": row[2], "tokens_out": row[3], "events": events}


def run_query(sql: str) -> list[dict[str, Any]]:
    if not sql.lstrip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed")
    init_db()
    with sqlite3.connect(db_path()) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql)]


def export_sessions(fmt: str) -> int:
    rows = list_sessions(None, None)
    if fmt == "json":
        print_json(json_envelope(True, "sessions export", {"sessions": rows}))
        return 0
    fieldnames = ["id", "start", "end", "project", "model", "cost", "tokens_in", "tokens_out"]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Record and query Claude Code session logs")
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("--session-dir", type=Path, default=session_log_dir())
    record.add_argument("--json", action="store_true")
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--project")
    list_cmd.add_argument("--since", default="7d")
    list_cmd.add_argument("--json", action="store_true")
    stats_cmd = sub.add_parser("stats")
    stats_cmd.add_argument("--json", action="store_true")
    query = sub.add_parser("query")
    query.add_argument("sql")
    query.add_argument("--json", action="store_true")
    export = sub.add_parser("export")
    export.add_argument("--format", choices=["csv", "json"], default="json")
    args = parser.parse_args()

    try:
        if args.command == "record":
            if not args.session_dir.exists():
                raise FileNotFoundError(f"session dir not found: {args.session_dir}")
            data = record_sessions(args.session_dir)
            print_json(json_envelope(True, "sessions record", data)) if args.json else print(data)
            return 0
        if args.command == "list":
            data = {"sessions": list_sessions(args.project, args.since)}
            print_json(json_envelope(True, "sessions list", data)) if args.json else print(json.dumps(data, indent=2))
            return 0
        if args.command == "stats":
            data = stats()
            print_json(json_envelope(True, "sessions stats", data)) if args.json else print(json.dumps(data, indent=2))
            return 0
        if args.command == "query":
            data = {"rows": run_query(args.sql)}
            print_json(json_envelope(True, "sessions query", data)) if args.json else print(json.dumps(data, indent=2))
            return 0
        if args.command == "export":
            return export_sessions(args.format)
    except FileNotFoundError as exc:
        print_json(json_envelope(False, f"sessions {args.command}", None, {"code": "SESSION_DIR_NOT_FOUND", "message": str(exc)}))
        return 1
    except ValueError as exc:
        print_json(json_envelope(False, f"sessions {args.command}", None, {"code": "QUERY_NOT_ALLOWED", "message": str(exc)}))
        return 1
    except sqlite3.Error as exc:
        print_json(json_envelope(False, f"sessions {args.command}", None, {"code": "SQLITE_ERROR", "message": str(exc)}))
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
