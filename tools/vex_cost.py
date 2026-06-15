#!/usr/bin/env python3
"""VEX Cost Tracker — Cost tracking and analytics for Claude Code sessions.

Usage:
    python vex_cost.py report [--days N] [--project NAME]
    python vex_cost.py budget set --amount AMOUNT [--period daily|monthly]
    python vex_cost.py budget status
    python vex_cost.py track [--session FILE]
    python vex_cost.py models
    python vex_cost.py export [--format csv|json] [--output FILE]
"""

import argparse
import csv
import io
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

SESSIONS_ROOT = os.path.expanduser("~/.claude/projects")
BUDGET_FILE = os.path.expanduser("~/.vex/budget.json")
USAGE_FILE = os.path.expanduser("~/.vex/usage.json")

MODELS = {
    "claude-opus-4-6": {"input_per_m": 15.0, "output_per_m": 75.0, "tier": "architecture"},
    "claude-sonnet-4-6": {"input_per_m": 3.0, "output_per_m": 15.0, "tier": "coding"},
    "claude-haiku-3-5": {"input_per_m": 0.25, "output_per_m": 1.25, "tier": "exploration"},
}


def ensure_vex_dir():
    d = Path.home() / ".vex"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(path, default=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def save_json(path, data):
    ensure_vex_dir()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


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


def parse_session_costs(filepath):
    """Extract token usage and costs from a session JSONL file."""
    records = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Look for usage/token data in various formats
                usage = None
                model = None
                timestamp = entry.get("timestamp", entry.get("ts", ""))

                # Direct usage field
                if "usage" in entry:
                    usage = entry["usage"]
                    model = entry.get("model", entry.get("modelId", ""))

                # In message wrapper
                msg = entry.get("message", {})
                if isinstance(msg, dict):
                    if "usage" in msg:
                        usage = msg["usage"]
                        model = msg.get("model", model)
                    if "model" in msg and not model:
                        model = msg["model"]

                # Cost field
                cost = entry.get("cost", entry.get("cost_usd", None))

                if usage or cost:
                    input_tokens = 0
                    output_tokens = 0
                    if isinstance(usage, dict):
                        input_tokens = usage.get("input_tokens", usage.get("inputTokens", 0))
                        output_tokens = usage.get("output_tokens", usage.get("outputTokens", 0))

                    # Calculate cost if not provided
                    if cost is None and (input_tokens or output_tokens):
                        cost = compute_cost(model, input_tokens, output_tokens)

                    records.append({
                        "timestamp": timestamp,
                        "model": model or "unknown",
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "cost": float(cost) if cost else 0.0,
                    })
    except (OSError, PermissionError):
        pass
    return records


def compute_cost(model, input_tokens, output_tokens):
    """Compute cost based on model pricing."""
    model_lower = (model or "").lower()
    pricing = None
    for mkey, mval in MODELS.items():
        if mkey in model_lower or model_lower in mkey:
            pricing = mval
            break
    if not pricing:
        # Default to sonnet pricing
        pricing = MODELS["claude-sonnet-4-6"]

    input_cost = (input_tokens / 1_000_000) * pricing["input_per_m"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_m"]
    return round(input_cost + output_cost, 6)


def ascii_bar(value, max_value, width=40):
    """Render an ASCII bar chart element."""
    if max_value <= 0:
        return ""
    filled = int((value / max_value) * width)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def ascii_chart(data, title="", width=50, height=10):
    """Render a simple ASCII bar chart."""
    if not data:
        return "(no data)"

    lines = []
    if title:
        lines.append(title)
        lines.append("=" * len(title))

    max_val = max(v for _, v in data) if data else 1
    if max_val == 0:
        max_val = 1

    label_width = max(len(str(k)) for k, _ in data) if data else 0
    label_width = min(label_width, 20)

    for key, val in data:
        label = str(key)[:label_width].rjust(label_width)
        bar = ascii_bar(val, max_val, width)
        lines.append(f"{label} |{bar}| ${val:.4f}")

    return "\n".join(lines)


def cmd_report(args):
    """Generate cost report."""
    session_files = find_session_files(args.project)
    if not session_files:
        print(f"No session files found at {SESSIONS_ROOT}")
        return

    all_records = []
    project_costs = defaultdict(float)
    daily_costs = defaultdict(float)
    model_costs = defaultdict(float)
    total_input = 0
    total_output = 0

    cutoff = None
    if args.days:
        cutoff = datetime.now() - timedelta(days=args.days)

    for proj_name, filepath in session_files:
        records = parse_session_costs(filepath)
        for rec in records:
            # Date filtering
            if cutoff and rec["timestamp"]:
                try:
                    ts = rec["timestamp"]
                    if isinstance(ts, str):
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if dt.timestamp() < cutoff.timestamp():
                            continue
                    elif isinstance(ts, (int, float)):
                        if ts < cutoff.timestamp():
                            continue
                except (ValueError, TypeError):
                    pass

            all_records.append(rec)
            project_costs[proj_name] += rec["cost"]
            model_costs[rec["model"]] += rec["cost"]
            total_input += rec["input_tokens"]
            total_output += rec["output_tokens"]

            if rec["timestamp"]:
                try:
                    ts = rec["timestamp"]
                    if isinstance(ts, str):
                        day = ts[:10]
                    else:
                        day = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    daily_costs[day] += rec["cost"]
                except (ValueError, TypeError):
                    pass

    total_cost = sum(r["cost"] for r in all_records)

    print(f"\n{'='*60}")
    print(f"  VEX Cost Report")
    if args.days:
        print(f"  Period: last {args.days} day(s)")
    if args.project:
        print(f"  Project: {args.project}")
    print(f"{'='*60}\n")

    print(f"Total sessions analyzed: {len(session_files)}")
    print(f"Total API calls: {len(all_records)}")
    print(f"Total input tokens:  {total_input:>14,}")
    print(f"Total output tokens: {total_output:>14,}")
    print(f"Total cost: ${total_cost:.4f}")

    # Budget status
    budget = load_json(BUDGET_FILE, {})
    if budget:
        daily_limit = budget.get("daily_limit", 0)
        monthly_limit = budget.get("monthly_limit", 0)
        today = datetime.now().strftime("%Y-%m-%d")
        today_cost = daily_costs.get(today, 0)

        if daily_limit:
            pct = (today_cost / daily_limit * 100) if daily_limit else 0
            print(f"\nDaily budget: ${today_cost:.4f} / ${daily_limit:.2f} ({pct:.0f}%)")
            if pct >= budget.get("alert_threshold_pct", 80):
                print("  ⚠ WARNING: Approaching daily limit!")
        if monthly_limit:
            month_cost = sum(v for k, v in daily_costs.items() if k[:7] == today[:7])
            pct = (month_cost / monthly_limit * 100) if monthly_limit else 0
            print(f"Monthly budget: ${month_cost:.4f} / ${monthly_limit:.2f} ({pct:.0f}%)")
            if pct >= budget.get("alert_threshold_pct", 80):
                print("  ⚠ WARNING: Approaching monthly limit!")

    # Per-project breakdown
    if project_costs:
        chart_data = sorted(project_costs.items(), key=lambda x: x[1], reverse=True)
        print(f"\nCost by project:")
        print(ascii_chart(chart_data[:15], width=30))

    # Per-model breakdown
    if model_costs:
        chart_data = sorted(model_costs.items(), key=lambda x: x[1], reverse=True)
        print(f"\nCost by model:")
        print(ascii_chart(chart_data, width=30))

    # Daily trend
    if daily_costs and len(daily_costs) > 1:
        chart_data = sorted(daily_costs.items())[-14:]  # Last 14 days
        print(f"\nDaily cost trend (last {len(chart_data)} days):")
        print(ascii_chart(chart_data, width=30))


def cmd_budget_set(args):
    """Set budget limits."""
    budget = load_json(BUDGET_FILE, {"alert_threshold_pct": 80})

    if args.period == "daily":
        budget["daily_limit"] = args.amount
        print(f"Daily budget set to ${args.amount:.2f}")
    else:
        budget["monthly_limit"] = args.amount
        print(f"Monthly budget set to ${args.amount:.2f}")

    save_json(BUDGET_FILE, budget)


def cmd_budget_status(args):
    """Show current budget status."""
    budget = load_json(BUDGET_FILE, {})
    if not budget:
        print("No budget configured. Use: budget set --amount 10.00 --period daily")
        return

    # Load usage
    usage = load_json(USAGE_FILE, {"daily": {}, "monthly": {}})
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = today[:7]

    daily_limit = budget.get("daily_limit", 0)
    monthly_limit = budget.get("monthly_limit", 0)
    daily_spent = usage.get("daily", {}).get(today, 0)
    monthly_spent = usage.get("monthly", {}).get(this_month, 0)
    threshold = budget.get("alert_threshold_pct", 80)

    print(f"\n{'='*40}")
    print(f"  Budget Status")
    print(f"{'='*40}\n")

    if daily_limit:
        pct = (daily_spent / daily_limit * 100) if daily_limit else 0
        bar = ascii_bar(min(daily_spent, daily_limit), daily_limit, 30)
        print(f"Daily ({today}):")
        print(f"  {bar}")
        print(f"  ${daily_spent:.4f} / ${daily_limit:.2f} ({pct:.1f}%)")
        if pct >= threshold:
            print(f"  ⚠ Above {threshold}% threshold!")
        remaining = max(0, daily_limit - daily_spent)
        print(f"  Remaining: ${remaining:.4f}")

    if monthly_limit:
        pct = (monthly_spent / monthly_limit * 100) if monthly_limit else 0
        bar = ascii_bar(min(monthly_spent, monthly_limit), monthly_limit, 30)
        print(f"\nMonthly ({this_month}):")
        print(f"  {bar}")
        print(f"  ${monthly_spent:.4f} / ${monthly_limit:.2f} ({pct:.1f}%)")
        if pct >= threshold:
            print(f"  ⚠ Above {threshold}% threshold!")
        remaining = max(0, monthly_limit - monthly_spent)
        print(f"  Remaining: ${remaining:.4f}")

    if not daily_limit and not monthly_limit:
        print("No limits set.")


def cmd_track(args):
    """Track a specific session or update usage records."""
    if args.session:
        filepath = Path(args.session)
        if not filepath.exists():
            print(f"Session not found: {filepath}")
            return
        records = parse_session_costs(filepath)
    else:
        # Track all sessions
        session_files = find_session_files()
        records = []
        for _, fp in session_files:
            records.extend(parse_session_costs(fp))

    if not records:
        print("No usage records found.")
        return

    # Update usage file
    usage = load_json(USAGE_FILE, {"daily": {}, "monthly": {}})
    for rec in records:
        ts = rec.get("timestamp", "")
        if isinstance(ts, str) and len(ts) >= 10:
            day = ts[:10]
            month = day[:7]
        else:
            day = datetime.now().strftime("%Y-%m-%d")
            month = day[:7]

        usage["daily"][day] = usage.get("daily", {}).get(day, 0) + rec["cost"]
        usage["monthly"][month] = usage.get("monthly", {}).get(month, 0) + rec["cost"]

    save_json(USAGE_FILE, usage)

    total = sum(r["cost"] for r in records)
    print(f"Tracked {len(records)} records, total: ${total:.4f}")

    # Budget check
    budget = load_json(BUDGET_FILE, {})
    threshold = budget.get("alert_threshold_pct", 80)
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = today[:7]

    if budget.get("daily_limit") and usage["daily"].get(today, 0) > budget["daily_limit"] * threshold / 100:
        print(f"⚠ ALERT: Daily spend exceeds {threshold}% of budget!")
    if budget.get("monthly_limit") and usage["monthly"].get(this_month, 0) > budget["monthly_limit"] * threshold / 100:
        print(f"⚠ ALERT: Monthly spend exceeds {threshold}% of budget!")


def cmd_models(args):
    """Display model pricing information."""
    print(f"\n{'='*65}")
    print(f"  VEX Model Pricing")
    print(f"{'='*65}\n")

    print(f"{'Model':<25} {'Input/M':>10} {'Output/M':>10} {'Tier':<15}")
    print("-" * 65)

    for model_id, info in MODELS.items():
        inp = info["input_per_m"]
        out = info["output_per_m"]
        tier = info["tier"]
        print(f"{model_id:<25} ${inp:>8.2f} ${out:>8.2f} {tier:<15}")

    print(f"\nTask Routing:")
    print(f"  architecture -> claude-opus-4-6")
    print(f"  coding       -> claude-sonnet-4-6")
    print(f"  exploration  -> claude-haiku-3-5")

    # Cost comparison
    print(f"\nCost comparison (1M tokens in + 1M tokens out):")
    for model_id, info in MODELS.items():
        total = info["input_per_m"] + info["output_per_m"]
        print(f"  {model_id}: ${total:.2f}")


def cmd_export(args):
    """Export cost data."""
    session_files = find_session_files()
    all_records = []

    for proj_name, filepath in session_files:
        records = parse_session_costs(filepath)
        for rec in records:
            rec["project"] = proj_name
            all_records.append(rec)

    if not all_records:
        print("No data to export.")
        return

    output = args.output

    if args.format == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["timestamp", "project", "model",
                                                   "input_tokens", "output_tokens", "cost"])
        writer.writeheader()
        writer.writerows(all_records)
        content = buf.getvalue()
    else:
        content = json.dumps(all_records, indent=2)

    if output:
        Path(output).write_text(content, encoding="utf-8")
        print(f"Exported {len(all_records)} records to {output}")
    else:
        print(content)


def main():
    parser = argparse.ArgumentParser(
        description="VEX Cost Tracker — Session cost analytics"
    )
    sub = parser.add_subparsers(dest="command")

    # report
    p_report = sub.add_parser("report", help="Generate cost report")
    p_report.add_argument("--days", type=int, help="Limit to last N days")
    p_report.add_argument("--project", help="Filter by project name")

    # budget
    p_budget = sub.add_parser("budget", help="Budget management")
    budget_sub = p_budget.add_subparsers(dest="budget_cmd")
    p_budget_set = budget_sub.add_parser("set", help="Set budget limit")
    p_budget_set.add_argument("--amount", type=float, required=True, help="Amount in USD")
    p_budget_set.add_argument("--period", choices=["daily", "monthly"], default="monthly",
                              help="Budget period (default: monthly)")
    budget_sub.add_parser("status", help="Show budget status")

    # track
    p_track = sub.add_parser("track", help="Track session costs")
    p_track.add_argument("--session", help="Specific session file to track")

    # models
    sub.add_parser("models", help="Show model pricing")

    # export
    p_export = sub.add_parser("export", help="Export cost data")
    p_export.add_argument("--format", choices=["csv", "json"], default="json", help="Export format")
    p_export.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    if args.command == "report":
        cmd_report(args)
    elif args.command == "budget":
        if args.budget_cmd == "set":
            cmd_budget_set(args)
        elif args.budget_cmd == "status":
            cmd_budget_status(args)
        else:
            p_budget.print_help()
    elif args.command == "track":
        cmd_track(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
