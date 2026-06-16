import datetime
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from urllib.parse import urlencode

from flask import Flask, Response, jsonify, redirect, render_template, request

PROJECT_ROOT = Path(os.path.abspath(__file__)).parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
SKILLS_DIR = PROJECT_ROOT / "skills"
CONTEXTS_DIR = PROJECT_ROOT / "contexts"
RULES_DIR = PROJECT_ROOT / "rules"
COST_LOG_PATH = Path.home() / ".claude" / "vex-costs.jsonl"
MAX_READ_BYTES = 128_000
AUTH_TOKEN = secrets.token_urlsafe(32)


@dataclass(frozen=True)
class CatalogItem:
    name: str
    category: str
    path: str
    title: str
    description: str
    tools: tuple[str, ...]
    size_bytes: int


@dataclass(frozen=True)
class CostRecord:
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@dataclass(frozen=True)
class CostSummary:
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    record_count: int
    skipped_lines: int
    by_model: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class HealthStatus:
    status: str
    checked_at: str
    checks: tuple[dict[str, Any], ...]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata: dict[str, str] = {}
    body_start = 1
    for index in range(1, len(lines)):
        line = lines[index]
        if line.strip() == "---":
            body_start = index + 1
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("'\"")
    return metadata, "\n".join(lines[body_start:])


def read_text_head(path: Path) -> str:
    try:
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")[:MAX_READ_BYTES]
    except OSError:
        return ""


def first_body_line(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:200]
    return ""


def list_agents() -> list[CatalogItem]:
    if not AGENTS_DIR.is_dir():
        return []

    agents: list[CatalogItem] = []
    for root, _, files in os.walk(AGENTS_DIR):
        root_path = Path(root)
        for filename in files:
            if not filename.endswith(".md"):
                continue

            file_path = root_path / filename
            text = read_text_head(file_path)
            metadata, body = parse_frontmatter(text)
            description = metadata.get("description", "") or first_body_line(body)
            tools = tuple(tool.strip() for tool in metadata.get("tools", "*").split(","))
            category = root_path.name if root_path != AGENTS_DIR else "core"
            agents.append(
                CatalogItem(
                    name=file_path.stem,
                    category=category,
                    path=str(file_path.relative_to(PROJECT_ROOT)),
                    title=metadata.get("name", file_path.stem),
                    description=description,
                    tools=tools,
                    size_bytes=file_path.stat().st_size,
                )
            )

    return sorted(agents, key=lambda item: (item.category, item.name))


def list_skills() -> list[CatalogItem]:
    if not SKILLS_DIR.is_dir():
        return []

    skills: list[CatalogItem] = []
    for root, _, files in os.walk(SKILLS_DIR):
        root_path = Path(root)
        if "SKILL.md" not in files:
            continue

        file_path = root_path / "SKILL.md"
        text = read_text_head(file_path)
        title = root_path.name
        description = ""
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
            elif stripped and not stripped.startswith("#"):
                description = stripped[:200]
                break

        category = root_path.parent.name if root_path.parent != SKILLS_DIR else "domain"
        skills.append(
            CatalogItem(
                name=root_path.name,
                category=category,
                path=str(file_path.relative_to(PROJECT_ROOT)),
                title=title,
                description=description,
                tools=(),
                size_bytes=file_path.stat().st_size,
            )
        )

    return sorted(skills, key=lambda item: (item.category, item.name))


def list_memory_sources() -> list[CatalogItem]:
    items: list[CatalogItem] = []
    for directory, category in ((CONTEXTS_DIR, "context"), (RULES_DIR, "rule")):
        if not directory.is_dir():
            continue

        for root, _, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(".md"):
                    continue

                file_path = Path(root) / filename
                text = read_text_head(file_path)
                items.append(
                    CatalogItem(
                        name=filename,
                        category=category,
                        path=str(file_path.relative_to(PROJECT_ROOT)),
                        title=filename,
                        description=text.strip()[:300],
                        tools=(),
                        size_bytes=file_path.stat().st_size,
                    )
                )

    return sorted(items, key=lambda item: (item.category, item.name))


def parse_cost_log() -> tuple[list[CostRecord], CostSummary]:
    if not COST_LOG_PATH.is_file():
        return [], CostSummary(0.0, 0, 0, 0, 0, ())

    records: list[CostRecord] = []
    skipped_lines = 0
    total_cost_usd = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    by_model: dict[str, float] = {}

    with COST_LOG_PATH.open("r", encoding="utf-8", errors="replace") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue

            try:
                record = parse_cost_record(line)
            except (TypeError, ValueError, json.JSONDecodeError):
                skipped_lines += 1
                continue

            records.append(record)
            total_cost_usd += record.cost_usd
            total_input_tokens += record.input_tokens
            total_output_tokens += record.output_tokens
            by_model[record.model] = by_model.get(record.model, 0.0) + record.cost_usd

    summary = CostSummary(
        total_cost_usd=total_cost_usd,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        record_count=len(records),
        skipped_lines=skipped_lines,
        by_model=tuple(sorted(by_model.items(), key=lambda item: item[1], reverse=True)),
    )
    return records, summary


def parse_cost_record(line: str) -> CostRecord:
    raw = json.loads(line)
    message = raw.get("message", {}) if isinstance(raw.get("message"), dict) else {}
    usage = raw.get("usage", {}) if isinstance(raw.get("usage"), dict) else {}
    if not usage:
        usage = message.get("usage", {}) if isinstance(message.get("usage"), dict) else {}

    timestamp = str(raw.get("timestamp", raw.get("ts", "")))
    model = str(raw.get("model", raw.get("modelId", message.get("model", "unknown"))))
    input_tokens = int(usage.get("input_tokens", usage.get("inputTokens", 0)))
    output_tokens = int(usage.get("output_tokens", usage.get("outputTokens", 0)))
    cost_usd = float(raw.get("cost_usd", raw.get("cost", 0.0)))
    if cost_usd == 0.0 and (input_tokens > 0 or output_tokens > 0):
        cost_usd = estimate_cost_usd(model, input_tokens, output_tokens)

    return CostRecord(timestamp, model, input_tokens, output_tokens, cost_usd)


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    normalized_model = model.lower()
    if "opus" in normalized_model:
        return (input_tokens * 15.0 / 1_000_000) + (output_tokens * 75.0 / 1_000_000)
    if "haiku" in normalized_model:
        return (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000)
    return (input_tokens * 3.0 / 1_000_000) + (output_tokens * 15.0 / 1_000_000)


def get_health() -> HealthStatus:
    checked_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    checks: list[dict[str, Any]] = []
    has_errors = False
    has_warnings = False

    for directory, name in ((PROJECT_ROOT, "project_root"), (AGENTS_DIR, "agents_dir"), (SKILLS_DIR, "skills_dir")):
        if directory.is_dir():
            checks.append({"name": name, "status": "ok", "detail": "present"})
        else:
            checks.append({"name": name, "status": "error", "detail": "missing"})
            has_errors = True

    if COST_LOG_PATH.is_file():
        checks.append({"name": "cost_log", "status": "ok", "detail": "readable"})
    else:
        checks.append({"name": "cost_log", "status": "warn", "detail": "missing (optional)"})
        has_warnings = True

    status = "error" if has_errors else "warn" if has_warnings else "ok"
    return HealthStatus(status=status, checked_at=checked_at, checks=tuple(checks))


def token_matches(candidate: str) -> bool:
    return bool(candidate) and secrets.compare_digest(AUTH_TOKEN, candidate)


def is_authorized() -> bool:
    cookie_token = request.cookies.get("vex_dashboard_token", "")
    auth_header = request.headers.get("Authorization", "")
    bearer_token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else ""
    return token_matches(cookie_token) or token_matches(bearer_token)


def query_token_matches() -> bool:
    return token_matches(request.args.get("token", ""))


def clean_request_url() -> str:
    clean_args = [(key, value) for key, value in request.args.items(multi=True) if key != "token"]
    query_string = urlencode(clean_args)
    return f"{request.path}?{query_string}" if query_string else request.path


def unauthorized_response() -> tuple[Response, int]:
    return jsonify({"error": "Unauthorized", "hint": "Use Authorization: Bearer <token>"}), 401


def print_startup_token() -> None:
    print("\n" + "=" * 50)
    print("VEX Dashboard running")
    print(f"Access token: {AUTH_TOKEN}")
    print(f"Use ?token={AUTH_TOKEN} or Authorization: Bearer {AUTH_TOKEN}")
    print("=" * 50 + "\n")


def create_app() -> Flask:
    app = Flask(__name__)

    @app.before_request
    def enforce_auth() -> Response | tuple[Response, int] | None:
        if request.path.startswith("/static/"):
            return None
        if is_authorized():
            return None
        if query_token_matches():
            response = redirect(clean_request_url())
            response.set_cookie("vex_dashboard_token", AUTH_TOKEN, httponly=True, samesite="Strict")
            return response
        return unauthorized_response()

    @app.after_request
    def add_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://unpkg.com; style-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'"
        return response

    @app.route("/")
    def index() -> str:
        agents = list_agents()
        skills = list_skills()
        memory_items = list_memory_sources()
        _, cost_summary = parse_cost_log()
        health = get_health()
        return render_template(
            "overview.html",
            agents_count=len(agents),
            skills_count=len(skills),
            memory_count=len(memory_items),
            cost_summary=cost_summary,
            health=health,
        )

    @app.route("/agents")
    def agents_route() -> str:
        return render_template("agents.html", agents=list_agents())

    @app.route("/skills")
    def skills_route() -> str:
        return render_template("skills.html", skills=list_skills())

    @app.route("/costs")
    def costs_route() -> str:
        records, cost_summary = parse_cost_log()
        recent_records = sorted(records, key=lambda record: record.timestamp, reverse=True)[:50]
        return render_template("costs.html", cost_summary=cost_summary, recent_records=recent_records)

    @app.route("/memory")
    def memory_route() -> str:
        return render_template("memory.html", memory_items=list_memory_sources())

    @app.route("/health")
    def health_route() -> Response | str:
        health = get_health()
        if request.headers.get("HX-Request"):
            return render_template("health_partial.html", health=health)
        if "application/json" in request.headers.get("Accept", ""):
            return jsonify(
                {
                    "status": health.status,
                    "checked_at": health.checked_at,
                    "checks": list(health.checks),
                }
            )
        return render_template("health_partial.html", health=health)

    print_startup_token()
    return app


if __name__ == "__main__":
    dashboard_app = create_app()
    print("Starting VEX dashboard on http://127.0.0.1:7777")
    dashboard_app.run(host="127.0.0.1", port=7777, debug=False, threaded=True)
