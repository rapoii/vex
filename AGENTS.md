# VEX Agent Orchestration Guide

VEX agents are small, typed roles that operate through harness adapters. Claude Code is the first supported target; other harnesses must implement the same manifest contract before receiving first-class packs.

## Agent groups

| Group | Purpose | Examples |
| --- | --- | --- |
| Planning | Turn broad goals into scoped work | planner, architect, product-planner |
| Build | Implement features and fixes | feature-builder, refactorer, migrator |
| Quality | Review, test, and verify changes | code-reviewer, tdd-guide, e2e-runner |
| Safety | Check security and operational risk | security-reviewer, secret-scanner |
| Intelligence | Improve harness behavior | skill-miner, cost-analyst, memory-curator |

## Default workflow

1. Use `planner` for complex features, migrations, or multi-file changes.
2. Use `architect` for component boundaries, install paths, data flow, and cross-harness decisions.
3. Use `tdd-guide` before adding behavior or validation logic.
4. Use implementation agents only after scope is clear.
5. Use `code-reviewer` after code or docs change.
6. Use `security-reviewer` before publishing, installing hooks, or changing trust boundaries.

## Parallelism

Run independent agents in parallel when their outputs do not depend on each other:

- planner and architect can run together for greenfield design.
- code-reviewer and security-reviewer can run together after files are created.
- cost-analyst and skill-miner can run together after run transcripts exist.

Do not parallelize agents that edit the same files unless they run in isolated worktrees and merge through review.

## Manifest contract

Each agent definition must include:

```yaml
name: short-kebab-case
summary: one-line purpose
harnesses:
  - claude-code
inputs:
  - project_path
outputs:
  - report
safety:
  writes_files: false
  touches_external_services: false
```

## Claude Code priority

Claude Code packs own canonical behavior in Phase 1 and Phase 2. Cross-harness adapters translate the canonical manifest later; they must not fork semantics unless a target cannot support a feature.

## Quality gates

- Every new agent needs a fixture or smoke test.
- Every agent that can write files needs review guidance and rollback notes.
- Every security-sensitive agent needs explicit authorization language.
- Every cost-heavy agent needs budget hints.
