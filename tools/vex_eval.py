from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAST_RESULTS = ROOT / ".vex-eval-last-results.json"


def grade_exact_match(result: subprocess.CompletedProcess[str], expected: str) -> tuple[bool, str]:
    actual = result.stdout.rstrip("\n")
    return actual == expected, f"stdout exact_match expected {expected!r} got {actual!r}"


def grade_contains(result: subprocess.CompletedProcess[str], expected: str) -> tuple[bool, str]:
    output = result.stdout + result.stderr
    return expected in output, f"output contains {expected!r}"


def grade_regex(result: subprocess.CompletedProcess[str], expected: str) -> tuple[bool, str]:
    output = result.stdout + result.stderr
    matched = re.search(expected, output) is not None
    return matched, f"output regex {expected!r}"


def grade_file_exists(result: subprocess.CompletedProcess[str], expected: str) -> tuple[bool, str]:
    path = Path(expected)
    if not path.is_absolute():
        path = ROOT / path
    exists = path.exists()
    return exists, f"file exists {os.fspath(path)!r}"


def grade_exit_code(result: subprocess.CompletedProcess[str], expected: str) -> tuple[bool, str]:
    try:
        expected_code = int(expected)
    except ValueError as exc:
        raise ValueError("exit_code expected must be integer") from exc
    return result.returncode == expected_code, f"exit_code expected {expected_code} got {result.returncode}"


GRADERS = {
    "exact_match": grade_exact_match,
    "contains": grade_contains,
    "regex": grade_regex,
    "file_exists": grade_file_exists,
    "exit_code": grade_exit_code,
}


def run_iteration(command: str, grader: str, expected: str, timeout: float | None) -> dict:
    argv = shlex.split(command)
    if not argv:
        raise ValueError("--cmd must not be empty")
    started = time.perf_counter()
    try:
        result = subprocess.run(
            argv,
            cwd=ROOT,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.perf_counter() - started
        passed, reason = GRADERS[grader](result, expected)
        return {
            "passed": passed,
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "reason": reason,
        }
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        return {
            "passed": False,
            "duration": duration,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "reason": f"timeout after {timeout} seconds",
        }


def summarize(iterations: list[dict]) -> dict:
    total = len(iterations)
    passed = sum(1 for item in iterations if item["passed"])
    avg_duration = sum(float(item["duration"]) for item in iterations) / total if total else 0.0
    return {
        "pass@k": passed > 0,
        "pass_rate": passed / total if total else 0.0,
        "avg_duration": avg_duration,
        "passed": passed,
        "total": total,
    }


def save_results(payload: dict) -> None:
    LAST_RESULTS.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_results() -> dict:
    data = json.loads(LAST_RESULTS.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("last results file is invalid")
    return data


def command_run(args: argparse.Namespace) -> int:
    if args.iterations < 1:
        raise ValueError("--iterations must be at least 1")
    if args.grader not in GRADERS:
        raise ValueError(f"unsupported grader: {args.grader}")
    iterations = [
        run_iteration(args.cmd, args.grader, str(args.expected), args.timeout)
        for _ in range(args.iterations)
    ]
    payload = {
        "tool": "vex_eval",
        "command": args.cmd,
        "grader": args.grader,
        "expected": str(args.expected),
        "metrics": summarize(iterations),
        "iterations": iterations,
    }
    save_results(payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["metrics"]["pass_rate"] == 1.0 else 1


def command_report(args: argparse.Namespace) -> int:
    payload = load_results()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VEX evaluation harness")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run command repeatedly and grade results")
    run_parser.add_argument("--cmd", required=True, help="Command to run")
    run_parser.add_argument("--iterations", type=int, default=1)
    run_parser.add_argument("--grader", choices=sorted(GRADERS), required=True)
    run_parser.add_argument("--expected", required=True)
    run_parser.add_argument("--timeout", type=float, default=None)
    run_parser.set_defaults(func=command_run)

    report_parser = subparsers.add_parser("report", help="Show last results")
    report_parser.set_defaults(func=command_report)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError, re.error) as exc:
        print(json.dumps({"tool": "vex_eval", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
