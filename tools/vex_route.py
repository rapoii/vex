#!/usr/bin/env python3
"""VEX Router — Route tasks to Claude model tiers.

Usage:
    python tools/vex_route.py --task "fix authentication bug" [--budget 0.50] [--json]
"""

import argparse
import json
import re

MODELS = {
    "opus": {
        "model": "claude-opus-4-6",
        "quality": "highest",
        "input_per_m": 15.0,
        "output_per_m": 75.0,
        "typical_tokens": 18000,
    },
    "sonnet": {
        "model": "claude-sonnet-4-6",
        "quality": "balanced",
        "input_per_m": 3.0,
        "output_per_m": 15.0,
        "typical_tokens": 12000,
    },
    "haiku": {
        "model": "claude-haiku-3-5",
        "quality": "fast",
        "input_per_m": 0.25,
        "output_per_m": 1.25,
        "typical_tokens": 6000,
    },
}

ROUTES = [
    ("security", "opus", ["security", "auth", "permission", "secret", "crypto", "xss", "csrf", "sql injection", "audit", "threat", "vulnerability"]),
    ("architecture/design", "opus", ["architecture", "architect", "design", "migration", "system", "strategy", "tradeoff", "proposal", "plan"]),
    ("simple fix", "haiku", ["typo", "rename", "small", "simple", "one-line", "format", "lint", "quick", "minor"]),
    ("exploration/search", "haiku", ["find", "search", "locate", "where", "grep", "explore", "inspect", "list", "summarize"]),
    ("coding/implementation", "sonnet", ["implement", "code", "build", "add", "fix", "refactor", "test", "update", "create", "change"]),
]

DOWNGRADE = {"opus": "sonnet", "sonnet": "haiku", "haiku": "haiku"}


def estimate_cost(tier):
    model = MODELS[tier]
    input_tokens = int(model["typical_tokens"] * 0.7)
    output_tokens = int(model["typical_tokens"] * 0.3)
    cost = (input_tokens / 1_000_000) * model["input_per_m"] + (output_tokens / 1_000_000) * model["output_per_m"]
    return round(cost, 4)


def match_route(task):
    text = task.lower()
    best = None
    best_hits = []
    for category, tier, terms in ROUTES:
        hits = [term for term in terms if re.search(r"\b" + re.escape(term) + r"\b", text)]
        if best is None or len(hits) > len(best_hits):
            best = (category, tier)
            best_hits = hits
    if best and best_hits:
        return best[0], best[1], best_hits
    return "coding/implementation", "sonnet", []


def apply_budget(tier, budget):
    if budget is None:
        return tier, []
    notes = []
    current = tier
    while estimate_cost(current) > budget and current != "haiku":
        previous = current
        current = DOWNGRADE[current]
        notes.append(f"Budget ${budget:.2f} below {previous} estimate; downgraded to {current}.")
    if estimate_cost(current) > budget:
        notes.append(f"Budget ${budget:.2f} below haiku estimate; keeping cheapest model.")
    return current, notes


def route_task(task, budget=None):
    category, initial_tier, hits = match_route(task)
    tier, budget_notes = apply_budget(initial_tier, budget)
    model = MODELS[tier]
    reasons = []
    if hits:
        reasons.append(f"Matched {category} keywords: " + ", ".join(hits) + ".")
    else:
        reasons.append("No strong keyword match; defaulted to coding/implementation.")
    if initial_tier != tier:
        reasons.extend(budget_notes)
    else:
        reasons.append(f"{tier} fits {category} workload.")
    return {
        "task": task,
        "category": category,
        "recommended_tier": tier,
        "recommended_model": model["model"],
        "quality": model["quality"],
        "estimated_cost_usd": estimate_cost(tier),
        "budget_usd": budget,
        "reasoning": reasons,
    }


def print_text(result):
    print(f"Recommended model: {result['recommended_model']} ({result['recommended_tier']})")
    print(f"Category: {result['category']}")
    print(f"Estimated cost: ${result['estimated_cost_usd']:.4f}")
    if result["budget_usd"] is not None:
        print(f"Budget: ${result['budget_usd']:.2f}")
    print("Reasoning:")
    for reason in result["reasoning"]:
        print(f"- {reason}")


def main():
    parser = argparse.ArgumentParser(description="Route tasks to appropriate Claude model tiers.")
    parser.add_argument("--task", required=True, help="Task description to route.")
    parser.add_argument("--budget", type=float, help="Maximum estimated spend in USD.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args()
    result = route_task(args.task, args.budget)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_text(result)


if __name__ == "__main__":
    main()
