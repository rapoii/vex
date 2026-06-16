---
name: multi-workflow
description: Full multi-model workflow with model selection per phase from plan to review.
argument-hint: "[feature | bug | project goal]"
---

# Multi Workflow

**Input**: $ARGUMENTS

## Purpose

Run a full feature or bug workflow with explicit model choice per phase.
Use this when planning, implementation, verification, and review all matter.
Keep phases visible so escalation happens for reasons, not habit.

## Workflow

1. Scope: Haiku or Sonnet inventories files, manifests, and existing docs.
2. Plan: Sonnet drafts plan; Opus resolves architecture and risk conflicts.
3. Tests: Sonnet or tdd-guide defines failing or targeted coverage.
4. Build: Sonnet implements smallest coherent slice.
5. Integrate: Opus handles cross-cutting conflicts or design reversals.
6. Verify: Sonnet runs targeted tests, app checks, and validators.
7. Review: code-reviewer checks correctness; security-reviewer checks risky paths.
8. Report: coordinator states diff, evidence, and remaining risks.

## Model Selection

- Haiku: cheap discovery, labels, lists, and repetitive checks.
- Sonnet: default for planning drafts, coding, tests, and validation.
- Opus: architecture, synthesis, hard bugs, and high-impact decisions.

## Rationale

Full workflows waste effort if every phase uses the largest model.
Most phases need competent execution, not maximum deliberation.
Escalate only when ambiguity, conflict, or blast radius is high.

## Guardrails

- Plan before complex changes.
- Use TDD for behavior, validators, installers, and generators.
- Review after edits.
- Security review hooks, installers, external calls, file writes, and secrets.

## Output

- Phase-by-phase result.
- Files changed and commands run.
- Review status and unresolved items.
