---
name: pre-commit-hooks
description: Configure local Git hooks for linting, formatting, type checking, and commit message validation before code reaches the remote.
argument-hint: "[tool | hook-type | config-file]"
metadata:
  origin: VEX
---

# Pre-Commit Hooks

Use this skill when setting up local pre-commit checks, enforcing code style automatically, or debugging failing git commits.

## Triggers

- User asks to set up Husky, lint-staged, or pre-commit framework.
- Fixing a broken hook that blocks all commits.
- Adding commit message linting (commitlint).
- Enforcing formatting and typechecks locally before CI.

## Inputs To Inspect

- `package.json` for `husky` or `lint-staged` config.
- `.husky/` directory for raw git hooks.
- `.pre-commit-config.yaml` for Python's pre-commit framework.
- `.git/hooks/` for unmanaged hooks.
- Commit message standards (`commitlint.config.js`).

## Hook Setup Strategy

1. Pick a framework: `husky` + `lint-staged` for Node, `pre-commit` for Python/polyglot.
2. Only run checks on *staged* files, not the whole repo, so commits are fast.
3. Apply formatters (`prettier`, `black`) and add them back to the index automatically.
4. Run fast linters (`eslint`, `ruff`) and block commit on failure.
5. Defer slow typechecks (`tsc`, `mypy`) to CI or run them without emitting.
6. Provide an escape hatch (`--no-verify`) but discourage its use.

## Husky + Lint-Staged (Node.js)

1. Install:
```bash
npm install --save-dev husky lint-staged
npx husky init
```

2. Configure `.husky/pre-commit`:
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

3. Configure `package.json` or `.lintstagedrc`:
```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md,yml,yaml}": [
      "prettier --write"
    ]
  }
}
```

## Commit Message Linting

1. Install:
```bash
npm install --save-dev @commitlint/{config-conventional,cli}
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js
```

2. Configure `.husky/commit-msg`:
```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx --no -- commitlint --edit ${1}
```

## Python Pre-Commit Framework

Configure `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      # Run the linter
      - id: ruff
        args: [ --fix ]
      # Run the formatter
      - id: ruff-format
```

Install the hooks:
```bash
pip install pre-commit
pre-commit install
```

## Verification Commands

```bash
# Node: Run lint-staged on all files to verify config
npx lint-staged --all

# Python: Run pre-commit on all files
pre-commit run --all-files

# Bypass hooks in emergency
git commit -m "fix: emergency hotfix" --no-verify
```

## Common Pitfalls

- Running `tsc` or `jest` on all files inside a pre-commit hook makes commits unbearably slow.
- Formatting files but failing to `git add` them back in older lint-staged setups.
- Hook scripts missing execution permissions (`chmod +x`).
- Developers globally bypassing hooks with alias `gc='git commit -n'` because they are too slow.
- Assuming local hooks replace CI. Hooks are a convenience; CI is the authority.

## Done Criteria

- Committing a badly formatted file automatically formats it.
- Committing a file with a syntax error blocks the commit.
- Checks take less than 5 seconds to run.
- CI pipeline mirrors the hook checks to catch `--no-verify` bypasses.
