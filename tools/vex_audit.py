#!/usr/bin/env python3
"""VEX Harness Audit — Score harness reliability.

Usage:
    python tools/vex_audit.py [--json] [--harness claude-code]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_AGENT_TERMS = {"planner", "code", "review", "security", "tdd", "debug", "refactor"}
DOMAIN_AGENT_TERMS = {"api", "database", "devops", "cloud", "mobile", "performance", "accessibility", "seo", "ml", "data"}
LANGUAGE_AGENT_TERMS = {"python", "typescript", "javascript", "go", "rust", "java", "kotlin", "swift", "ruby", "php", "csharp", "cpp", "dart", "fsharp"}
SKILL_CATEGORIES = {"build", "debug", "docs", "optimize", "plan", "refactor", "security", "tdd", "verify", "research"}
HOOK_EVENTS = {"PreToolUse", "PostToolUse", "Notification", "Stop", "SubagentStop", "PreCompact", "UserPromptSubmit"}
COMMON_RULES = {"coding-style", "development-workflow", "security", "testing", "code-review", "git-workflow", "agents"}
REQUIRED_CONFIG_FIELDS = {"id", "name", "version", "description"}


def clamp(value):
    return max(0, min(100, int(round(value))))


def markdown_files(path):
    if not path.exists():
        return []
    return [p for p in path.rglob("*.md") if p.is_file()]


def json_files(path):
    if not path.exists():
        return []
    return [p for p in path.rglob("*.json") if p.is_file()]


def line_count(path):
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def average_lines(files):
    if not files:
        return 0
    return sum(line_count(path) for path in files) / len(files)


def contains_any(name, terms):
    lowered = name.lower()
    return any(term in lowered for term in terms)


def score_agents():
    files = markdown_files(ROOT / "agents")
    names = [p.stem.lower() for p in files]
    count_score = min(len(files) / 20, 1) * 35
    avg = average_lines(files)
    quality_score = min(avg / 80, 1) * 30
    coverage = 0
    if any(contains_any(name, CORE_AGENT_TERMS) for name in names):
        coverage += 1
    if any(contains_any(name, DOMAIN_AGENT_TERMS) for name in names):
        coverage += 1
    if any(contains_any(name, LANGUAGE_AGENT_TERMS) for name in names):
        coverage += 1
    coverage_score = (coverage / 3) * 35
    score = clamp(count_score + quality_score + coverage_score)
    recommendations = []
    if len(files) < 20:
        recommendations.append("Add more specialized agents for core workflows, domains, and languages.")
    if avg < 50:
        recommendations.append("Expand thin agent definitions with triggers, workflow, outputs, and quality gates.")
    if coverage < 3:
        recommendations.append("Cover core, domain, and language agent categories.")
    return {"score": score, "count": len(files), "average_lines": round(avg, 1), "recommendations": recommendations}


def score_skills():
    files = markdown_files(ROOT / "skills")
    names = [p.parent.name.lower() if p.name == "SKILL.md" else p.stem.lower() for p in files]
    count_score = min(len(files) / 15, 1) * 35
    avg = average_lines(files)
    quality_score = min(avg / 90, 1) * 30
    covered = {cat for cat in SKILL_CATEGORIES if any(cat in name for name in names)}
    category_score = (len(covered) / len(SKILL_CATEGORIES)) * 35
    score = clamp(count_score + quality_score + category_score)
    recommendations = []
    missing = sorted(SKILL_CATEGORIES - covered)
    if len(files) < 15:
        recommendations.append("Add skills for repeated workflows and quality gates.")
    if avg < 60:
        recommendations.append("Expand skill docs with triggers, steps, validation, and outputs.")
    if missing:
        recommendations.append("Add missing skill categories: " + ", ".join(missing) + ".")
    return {"score": score, "count": len(files), "average_lines": round(avg, 1), "categories_covered": sorted(covered), "recommendations": recommendations}


def score_hooks():
    hook_dir = ROOT / "hooks"
    scripts = []
    if hook_dir.exists():
        scripts = [p for p in hook_dir.rglob("*") if p.is_file() and p.suffix in {".py", ".js", ".sh", ".ps1", ".json"}]
    text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in scripts if path.stat().st_size < 1_000_000)
    events = sorted(event for event in HOOK_EVENTS if event in text)
    controls = sum(1 for term in ["timeout", "max", "limit", "allow", "deny", "dry", "exit"] if term in text.lower())
    score = clamp(min(len(scripts) / 8, 1) * 35 + (len(events) / len(HOOK_EVENTS)) * 35 + min(controls / 5, 1) * 30)
    recommendations = []
    if not scripts:
        recommendations.append("Add hook scripts or templates.")
    if len(events) < 4:
        recommendations.append("Cover more Claude Code hook events.")
    if controls < 3:
        recommendations.append("Add runtime controls such as timeouts, limits, allowlists, and dry-run behavior.")
    return {"score": score, "scripts": len(scripts), "events_covered": events, "recommendations": recommendations}


def score_rules():
    files = markdown_files(ROOT / "rules")
    paths = [p.as_posix().lower() for p in files]
    frameworks = sorted({p.parts[-2] for p in files if len(p.parts) >= 2 and p.parent.name != "common"})
    common = sorted(rule for rule in COMMON_RULES if any(rule in path for path in paths))
    score = clamp(min(len(frameworks) / 6, 1) * 45 + (len(common) / len(COMMON_RULES)) * 55)
    recommendations = []
    missing = sorted(COMMON_RULES - set(common))
    if len(frameworks) < 6:
        recommendations.append("Add framework-specific rule packs for common stacks.")
    if missing:
        recommendations.append("Add common rules: " + ", ".join(missing) + ".")
    return {"score": score, "frameworks_covered": frameworks, "common_rules_present": common, "recommendations": recommendations}


def score_config():
    files = json_files(ROOT / "config") + json_files(ROOT / "adapters")
    valid = 0
    complete = 0
    invalid = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            valid += 1
            if isinstance(data, dict):
                keys = set(data)
                if REQUIRED_CONFIG_FIELDS <= keys or {"id", "version"} <= keys:
                    complete += 1
        except (OSError, json.JSONDecodeError):
            invalid.append(str(path.relative_to(ROOT)))
    valid_score = (valid / len(files)) * 60 if files else 0
    complete_score = (complete / len(files)) * 40 if files else 0
    recommendations = []
    if invalid:
        recommendations.append("Fix invalid JSON files: " + ", ".join(invalid) + ".")
    if complete < len(files):
        recommendations.append("Add complete id/name/version/description fields where applicable.")
    return {"score": clamp(valid_score + complete_score), "json_files": len(files), "valid_json": valid, "complete_fields": complete, "recommendations": recommendations}


def discover_tests():
    test_dir = ROOT / "tests"
    if not test_dir.exists():
        return []
    return [p for p in test_dir.rglob("test*") if p.is_file() and p.suffix in {".py", ".js", ".mjs", ".cjs"}]


def test_pass_rate():
    commands = []
    if (ROOT / "tests").exists():
        commands.append([sys.executable, "-m", "pytest", "tests"])
    if (ROOT / "package.json").exists():
        commands.append(["npm", "test", "--", "--runInBand"])
    attempted = 0
    passed = 0
    for command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=False)
            attempted += 1
            if result.returncode == 0:
                passed += 1
        except (OSError, subprocess.TimeoutExpired):
            attempted += 1
    if attempted == 0:
        return None
    return passed / attempted


def score_tests(run_tests=False):
    tests = discover_tests()
    count_score = min(len(tests) / 20, 1) * 45
    rate = test_pass_rate() if run_tests else None
    pass_score = 55 if rate is None else rate * 55
    score = clamp(count_score + pass_score)
    recommendations = []
    if len(tests) < 20:
        recommendations.append("Add tests for tools, adapters, hooks, installers, and generators.")
    if rate is not None and rate < 1:
        recommendations.append("Fix failing test commands before release.")
    return {"score": score, "count": len(tests), "pass_rate": None if rate is None else round(rate, 2), "recommendations": recommendations}


def audit(harness):
    categories = {
        "agents": score_agents(),
        "skills": score_skills(),
        "hooks": score_hooks(),
        "rules": score_rules(),
        "config": score_config(),
        "tests": score_tests(),
    }
    overall = clamp(sum(item["score"] for item in categories.values()) / len(categories))
    recommendations = []
    for name, item in categories.items():
        for rec in item["recommendations"][:2]:
            recommendations.append(f"{name}: {rec}")
    return {"harness": harness, "overall_score": overall, "categories": categories, "recommendations": recommendations[:12]}


def print_text(result):
    print(f"VEX Harness Audit: {result['harness']}")
    print(f"Overall score: {result['overall_score']}/100")
    print("")
    for name, item in result["categories"].items():
        print(f"{name.title()}: {item['score']}/100")
    if result["recommendations"]:
        print("\nRecommendations:")
        for rec in result["recommendations"]:
            print(f"- {rec}")


def main():
    parser = argparse.ArgumentParser(description="Score VEX harness reliability.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument("--harness", default="claude-code", help="Harness adapter id to label the audit.")
    args = parser.parse_args()
    result = audit(args.harness)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)


if __name__ == "__main__":
    main()
