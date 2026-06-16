---
name: multi-plan
description: Plan with Sonnet exploration and Opus architecture synthesis.
argument-hint: "[scope | issue | blank for current diff]"
---

# Multi Plan

**Input**: $ARGUMENTS

## Purpose

Build an implementation plan from multiple model perspectives before code changes.
Use this for ambiguous features, cross-cutting refactors, and risky migrations.
Keep final plan small enough to execute and verify.

## Workflow

1. Define scope from input, current branch, or issue text.
2. Send Sonnet to map files, constraints, and existing patterns.
3. Send Sonnet to identify tests, validators, and likely regressions.
4. Send Opus to assess architecture, tradeoffs, and irreversible risks.
5. Compare outputs for conflicts, missing files, and hidden dependencies.
6. Choose one plan with explicit non-goals and rollback path.
7. Convert plan into ordered tasks with validation commands.
8. Stop before editing unless user already authorized implementation.

## Model Selection

- Sonnet: fast exploration across files and normal engineering judgment.
- Opus: architecture synthesis, hard tradeoffs, security or data-loss risk.
- Haiku: optional inventory when only file lists or labels are needed.

## Rationale

Exploration benefits from speed and breadth.
Architecture benefits from deeper reasoning and conflict resolution.
Use Opus once for final decision, not for every lookup.

## Output

- Scope and assumptions.
- Ordered implementation steps.
- Critical files and tests.
- Risks, rollback, and open questions.
