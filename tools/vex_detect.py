#!/usr/bin/env python3
"""VEX Package Manager Detection — auto-detect project package manager."""
import argparse
import json
import os
import sys
from pathlib import Path

MANAGERS = [
    {"name": "bun", "lockfile": "bun.lockb", "install": "bun install", "build": "bun run build"},
    {"name": "pnpm", "lockfile": "pnpm-lock.yaml", "install": "pnpm install", "build": "pnpm build"},
    {"name": "yarn", "lockfile": "yarn.lock", "install": "yarn install", "build": "yarn build"},
    {"name": "npm", "lockfile": "package-lock.json", "install": "npm install", "build": "npm run build"},
    {"name": "poetry", "lockfile": "poetry.lock", "install": "poetry install", "build": "poetry build"},
    {"name": "pip", "lockfile": "requirements.txt", "install": "pip install -r requirements.txt", "build": "python setup.py build"},
    {"name": "cargo", "lockfile": "Cargo.lock", "install": "cargo build", "build": "cargo build --release"},
    {"name": "go", "lockfile": "go.sum", "install": "go mod download", "build": "go build ./..."},
]

def detect(directory: str) -> list[dict]:
    results = []
    for mgr in MANAGERS:
        lockpath = Path(directory) / mgr["lockfile"]
        if lockpath.exists():
            results.append({
                "manager": mgr["name"],
                "lockfile": str(lockpath),
                "install": mgr["install"],
                "build": mgr["build"],
            })
    return results

def main():
    parser = argparse.ArgumentParser(description="VEX Package Manager Detection")
    parser.add_argument("--dir", default=".", help="Project directory")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    results = detect(args.dir)

    if args.json:
        print(json.dumps({"detected": results, "count": len(results)}, indent=2))
    else:
        if not results:
            print("No package manager detected")
        else:
            for r in results:
                print(f"{r['manager']}: {r['lockfile']}")
                print(f"  install: {r['install']}")
                print(f"  build:   {r['build']}")

if __name__ == "__main__":
    main()
