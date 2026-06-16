---
name: multi-execute
description: Execute plans with model rotation by task type and verification depth.
argument-hint: "[plan | task list | blank for current plan]"
---

# Multi Execute

**Input**: $ARGUMENTS

## Purpose

Execute an approved plan by routing work to models by complexity.
Use this when tasks can be split into safe, reviewable chunks.
Keep integration controlled by one coordinator.

## Workflow

1. Parse plan into independent implementation tasks.
2. Assign simple edits and inventory checks to Haiku or Sonnet.
3. Assign normal code changes and tests to Sonnet.
4. Assign architecture conflicts and risky integration to Opus.
5. Land changes in smallest coherent order.
6. Run targeted tests after each behavior change.
7. Run broader validation once integration completes.
8. Send final diff to reviewer agents before reporting done.

## Model Selection

- Haiku: file inventory, repetitive markdown, simple mechanical edits.
- Sonnet: main implementation, tests, refactors, and build fixes.
- Opus: hard debugging, cross-subsystem decisions, final synthesis.

## Rationale

Most execution is pattern-following and should stay fast.
Escalation prevents expensive reasoning from being wasted on routine edits.
Opus handles places where wrong integration costs more than slower thinking.

## Guardrails

- Do not parallel edit same file from multiple agents.
- Keep destructive commands blocked unless user confirms.
- Prefer TDD for behavior changes.
- Preserve existing public contracts unless plan says otherwise.

## Output

- Files changed.
- Tests run and results.
- Review findings fixed or accepted risks.
