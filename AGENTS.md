# VEX Agent Orchestration Guide

VEX includes 39 agent definitions. VEX agents are small, typed roles that operate through harness adapters. Claude Code is the first supported target; other harnesses must implement the same manifest contract before receiving first-class packs.

## Agent groups

| Group | Purpose | Examples |
| --- | --- | --- |
| Planning | Turn broad goals into scoped work | brainstormer, planner, architect, product-planner |
| Coordination | Split approved plans into safe agent batches | subagent-coordinator |
| Build | Implement features and fixes | feature-builder, refactorer, migrator |
| Quality | Review, test, and verify changes | code-reviewer, tdd-guide, e2e-runner |
| Research | Find authoritative docs and source evidence | docs-lookup |
| Safety | Check security and operational risk | security-reviewer, secret-scanner |
| Domain | Review specialized implementation risks | database-reviewer, mle-reviewer, accessibility |
| Intelligence | Improve harness behavior | skill-miner, cost-analyst, memory-curator |

## Default workflow

1. Use `brainstormer` when user intent, success criteria, or product shape is unclear.
2. Use `planner` for complex features, migrations, or multi-file changes after scope is clear.
3. Use `architect` for component boundaries, install paths, data flow, and cross-harness decisions.
4. Use `tdd-guide` before adding behavior or validation logic.
5. Use `subagent-coordinator` to split approved plans into fresh subagent tasks with batch checkpoints.
6. Use `docs-lookup` when current external API or framework behavior must be verified.
7. Use implementation agents only after scope is clear.
8. Use `database-reviewer` or `mle-reviewer` for specialized persistence or ML risk.
9. Use `e2e-runner` when user-visible flows need proof.
10. Use `code-reviewer` after code or docs change.
11. Use `security-reviewer` before publishing, installing hooks, or changing trust boundaries.

## Parallelism

Run independent agents in parallel when their outputs do not depend on each other:

- brainstormer and architect can run together for early design options when product intent and system boundary are both unclear.
- planner and architect can run together for greenfield design.
- subagent-coordinator can batch independent implementation agents after plan approval.
- code-reviewer and security-reviewer can run together after files are created.
- cost-analyst and skill-miner can run together after run transcripts exist.

Do not parallelize agents that edit the same files unless they run in isolated worktrees and merge through review. Use `subagent-coordinator` to identify safe batches and required human checkpoints.

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
