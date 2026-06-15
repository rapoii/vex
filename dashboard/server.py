import json
import logging
import os
import secrets
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from flask import Flask, render_template, request, jsonify

# Config
PROJECT_ROOT = Path(os.path.abspath(__file__)).parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
SKILLS_DIR = PROJECT_ROOT / "skills"
CONTEXTS_DIR = PROJECT_ROOT / "contexts"
RULES_DIR = PROJECT_ROOT / "rules"
COST_LOG_PATH = Path.home() / ".claude" / "vex-costs.jsonl"

MAX_READ_BYTES = 128000

# Models
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
    checks: tuple[dict, ...]

# Parsers & File Readers
def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata = {}
    body_start = 1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body_start = i + 1
            break
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            metadata[k.strip()] = v.strip().strip("'\"")
    return metadata, "\n".join(lines[body_start:])

def read_text_head(path: Path) -> str:
    try:
        if not path.is_file():
            return ""
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(MAX_READ_BYTES)
    except Exception:
        return ""

def list_agents() -> List[CatalogItem]:
    if not AGENTS_DIR.is_dir():
        return []
    agents = []
    for root, _, files in os.walk(AGENTS_DIR):
        root_path = Path(root)
        for f in files:
            if f.endswith(".md"):
                file_path = root_path / f
                text = read_text_head(file_path)
                meta, body = parse_frontmatter(text)

                # Try to extract description from meta or first paragraph
                desc = meta.get("description", "")
                if not desc:
                    for line in body.splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            desc = line[:200]
                            break

                tools = tuple([t.strip() for t in meta.get("tools", "*").split(",")])
                cat = root_path.name if root_path != AGENTS_DIR else "core"
                rel = str(file_path.relative_to(PROJECT_ROOT))

                agents.append(CatalogItem(
                    name=file_path.stem,
                    category=cat,
                    path=rel,
                    title=meta.get("name", file_path.stem),
                    description=desc,
                    tools=tools,
                    size_bytes=file_path.stat().st_size
                ))
    agents.sort(key=lambda a: (a.category, a.name))
    return agents

def list_skills() -> List[CatalogItem]:
    if not SKILLS_DIR.is_dir():
        return []
    skills = []
    for root, _, files in os.walk(SKILLS_DIR):
        root_path = Path(root)
        if "SKILL.md" in files:
            file_path = root_path / "SKILL.md"
            text = read_text_head(file_path)

            # Simple header extraction
            title = root_path.name
            desc = ""
            for line in text.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                elif line.strip() and not line.startswith("#"):
                    desc = line.strip()[:200]
                    break

            cat = root_path.parent.name if root_path.parent != SKILLS_DIR else "domain"
            rel = str(file_path.relative_to(PROJECT_ROOT))

            skills.append(CatalogItem(
                name=root_path.name,
                category=cat,
                path=rel,
                title=title,
                description=desc,
                tools=(),
                size_bytes=file_path.stat().st_size
            ))
    skills.sort(key=lambda s: (s.category, s.name))
    return skills

def list_memory_sources() -> List[CatalogItem]:
    items = []
    dirs = [
        (CONTEXTS_DIR, "context"),
        (RULES_DIR, "rule"),
    ]
    for d, cat in dirs:
        if d.is_dir():
            for root, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".md"):
                        file_path = Path(root) / f
                        text = read_text_head(file_path)
                        rel = str(file_path.relative_to(PROJECT_ROOT))
                        desc = text.strip()[:300]
                        items.append(CatalogItem(
                            name=f,
                            category=cat,
                            path=rel,
                            title=f,
                            description=desc,
                            tools=(),
                            size_bytes=file_path.stat().st_size
                        ))
    items.sort(key=lambda i: (i.category, i.name))
    return items

def parse_cost_log() -> Tuple[List[CostRecord], CostSummary]:
    if not COST_LOG_PATH.is_file():
        return [], CostSummary(0.0, 0, 0, 0, 0, ())

    records = []
    skipped = 0
    total_cost = 0.0
    total_in = 0
    total_out = 0
    by_model = {}

    with open(COST_LOG_PATH, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                ts = data.get("timestamp", data.get("ts", ""))

                # Model extraction
                model = data.get("model", data.get("modelId", ""))
                if not model and "message" in data:
                    model = data["message"].get("model", "")

                # Usage extraction
                usage = data.get("usage", {})
                if not usage and "message" in data:
                    usage = data["message"].get("usage", {})

                i_tok = int(usage.get("input_tokens", usage.get("inputTokens", 0)))
                o_tok = int(usage.get("output_tokens", usage.get("outputTokens", 0)))

                # Cost extraction
                cost = float(data.get("cost_usd", data.get("cost", 0.0)))

                # Heuristic pricing if missing
                if cost == 0.0 and (i_tok > 0 or o_tok > 0):
                    if "opus" in model:
                        cost = (i_tok * 15.0 / 1e6) + (o_tok * 75.0 / 1e6)
                    elif "haiku" in model:
                        cost = (i_tok * 0.25 / 1e6) + (o_tok * 1.25 / 1e6)
                    else: # sonnet default
                        cost = (i_tok * 3.0 / 1e6) + (o_tok * 15.0 / 1e6)

                rec = CostRecord(ts, model, i_tok, o_tok, cost)
                records.append(rec)

                total_cost += cost
                total_in += i_tok
                total_out += o_tok
                by_model[model] = by_model.get(model, 0.0) + cost

            except Exception:
                skipped += 1

    sorted_models = tuple(sorted(by_model.items(), key=lambda x: x[1], reverse=True))
    summary = CostSummary(
        total_cost_usd=total_cost,
        total_input_tokens=total_in,
        total_output_tokens=total_out,
        record_count=len(records),
        skipped_lines=skipped,
        by_model=sorted_models
    )
    return records, summary

def get_health() -> HealthStatus:
    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    checks = []
    has_errors = False
    has_warns = False

    # Check Dirs
    for d, name in [(AGENTS_DIR, "agents_dir"), (SKILLS_DIR, "skills_dir"), (PROJECT_ROOT, "project_root")]:
        if d.is_dir():
            checks.append({"name": name, "status": "ok", "detail": "present"})
        else:
            checks.append({"name": name, "status": "error", "detail": "missing"})
            has_errors = True

    # Check Cost log
    if COST_LOG_PATH.is_file():
        checks.append({"name": "cost_log", "status": "ok", "detail": "readable"})
    else:
        checks.append({"name": "cost_log", "status": "warn", "detail": "missing (optional)"})
        has_warns = True

    status = "error" if has_errors else ("warn" if has_warns else "ok")
    return HealthStatus(status=status, checked_at=now, checks=tuple(checks))

# Flask App
def create_app():
    app = Flask(__name__)

# Generate auth token
AUTH_TOKEN = secrets.token_urlsafe(16)
print(f"
{'='*50}")
print(f"VEX Dashboard running!")
print(f"Access token: {AUTH_TOKEN}")
print(f"Use ?token={AUTH_TOKEN} or Authorization header")
print(f"{'='*50}
")

def check_auth():
    # Allow static files without auth
    if request.path.startswith('/static/'):
        return None
        
    token = request.args.get('token')
    auth_header = request.headers.get('Authorization')
    
    if token == AUTH_TOKEN:
        return None
    
    if auth_header and auth_header.startswith('Bearer ') and auth_header.split(' ')[1] == AUTH_TOKEN:
        return None
        
    return jsonify({"error": "Unauthorized"}), 401

@app.before_request
def enforce_auth():
    return check_auth()


    @app.after_request
    def add_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @app.route("/")
    def index():
        agents = list_agents()
        skills = list_skills()
        items = list_memory_sources()
        _, cost_sum = parse_cost_log()
        health = get_health()
        return render_template(
            "overview.html",
            agents_count=len(agents),
            skills_count=len(skills),
            memory_count=len(items),
            cost_summary=cost_sum,
            health=health
        )

    @app.route("/agents")
    def agents_route():
        agents = list_agents()
        return render_template("agents.html", agents=agents)

    @app.route("/skills")
    def skills_route():
        skills = list_skills()
        return render_template("skills.html", skills=skills)

    @app.route("/costs")
    def costs_route():
        records, summary = parse_cost_log()
        recent = sorted(records, key=lambda x: x.timestamp, reverse=True)[:50]
        return render_template("costs.html", cost_summary=summary, recent_records=recent)

    @app.route("/memory")
    def memory_route():
        items = list_memory_sources()
        return render_template("memory.html", memory_items=items)

    @app.route("/health")
    def health_route():
        health = get_health()
        if request.headers.get("HX-Request"):
            return render_template("health_partial.html", health=health)
        if request.headers.get("Accept", "").startswith("application/json"):
            return jsonify({
                "status": health.status,
                "checked_at": health.checked_at,
                "checks": health.checks
            })
        return render_template("health_partial.html", health=health)

    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting VEX dashboard on http://127.0.0.1:7777")
    app.run(host="127.0.0.1", port=7777, debug=False)