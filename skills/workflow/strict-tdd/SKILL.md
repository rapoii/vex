---
name: strict-tdd
description: Enforce non-negotiable RED/GREEN/REFACTOR development, including deleting pre-test code.
argument-hint: "[behavior | bug | feature]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["New behavior", "Bug fix", "Regression test", "User asks for strict TDD", "Implementation lacks tests"]
---

# Strict TDD Workflow

Use this skill when behavior changes and test-first discipline must be enforced.

This workflow adapts Superpowers-style test-driven development for VEX: RED first, GREEN minimal, REFACTOR safe, and delete production code written before failing tests.

## When to Activate

- New behavior will be implemented.
- Bug fix needs regression coverage.
- User asks for strict TDD.
- Agent started coding before tests.
- Plan acceptance criteria can become tests.
- Existing behavior needs characterization before refactor.
- Review finds untested logic.

## When Not to Activate

- Pure markdown docs with no behavior contract.
- Formatting-only change.
- Emergency hotfix where user explicitly waives tests.
- Test harness is absent and user asks only for exploratory spike.
- Generated file update where source test already covers output.

## Core Principles

### 1. RED Comes First

Write failing test before production change.

Run exact test.

Confirm failure is for expected reason.

Do not proceed on compile error unrelated to intended behavior.

### 2. GREEN Is Minimal

Write smallest production code that passes test.

Avoid extra abstractions.

Avoid speculative features.

Do not fix unrelated failures unless they block validation.

### 3. REFACTOR Preserves Green

Improve names, shape, duplication, and boundaries only after tests pass.

Run same tests after refactor.

If tests fail, revert or fix before continuing.

### 4. Delete Pre-Test Code

If production code was written before failing test, remove or revert it.

Then write test and watch it fail.

Do not rationalize pre-test code as prototype unless user explicitly switches to spike mode.

### 5. Behavior Over Implementation

Tests should prove observable behavior.

Avoid testing private functions, internal state, timing sleeps, or incidental markup.

## Workflow

### Step 1: Extract Behavior

Write behavior statement:

```text
When <action>, system should <observable result>, because <user outcome>.
```

Name boundary:

- CLI
- HTTP
- UI
- file operation
- pure function
- manifest validation
- hook payload

### Step 2: Find Test Location

Search existing tests.

Prefer nearby test file.

If no test file exists, create one following project runner conventions.

Do not invent new test framework without user approval.

### Step 3: Check For Pre-Test Code

Inspect current diff.

If production changes already exist for target behavior:

1. Inspect `git diff` for exact files and ownership.
2. Summarize what exists and whether it came from current agent, user, or another agent.
3. Ask before deleting or reverting anything not created by current agent in current turn.
4. Revert only current-agent changes when tool history proves they are fully recoverable.
5. Keep only test scaffolding if it does not implement behavior.
6. Run tests to verify behavior still absent.

This enforces test-first order without deleting user or other-agent work.

### Step 4: Write Failing Test

Add one focused test.

Test name describes behavior.

Good:

```text
test_rejects_worktree_cleanup_when_changes_are_dirty
```

Bad:

```text
test_issue_123
```

Include success path and failure path across separate tests when needed.

### Step 5: Run RED

Run narrow command.

Examples:

```bash
npm test -- --workflow-pack
pytest tests/test_install.py -q
node tests/test-workflow-pack.js
```

Confirm:

- Command fails.
- Failure points to missing behavior.
- Failure is not syntax, import, or environment issue unless that is behavior.

Record failure in notes.

### Step 6: Implement GREEN

Write minimal code.

Only touch files needed for failing test.

Prefer explicit logic.

Validate inputs at boundaries.

Avoid broad cleanup.

### Step 7: Run GREEN

Run same narrow command.

Confirm failing test now passes.

If another test fails, inspect whether regression caused it.

Do not skip tests.

### Step 8: Add Adjacent Cases

If acceptance criteria include edge cases, add tests one at a time.

For each case:

1. Add failing test.
2. Run RED.
3. Implement minimal change.
4. Run GREEN.

Do not batch many failing tests unless all are same missing public contract.

### Step 9: Refactor

Refactor only after tests green.

Allowed refactor:

- Rename unclear identifiers.
- Extract repeated logic with same meaning.
- Simplify conditionals.
- Split oversized function.
- Remove dead code.

Forbidden refactor:

- Add feature not under test.
- Change public behavior without test.
- Move files broadly without need.
- Introduce framework dependency for tiny helper.

### Step 10: Validate Wider Scope

After narrow GREEN, run broader validation.

Examples:

```bash
npm test
pytest -q
npm run validate
```

If full validation fails unrelated to change, report separately with evidence.

### Step 11: Review

Use code-reviewer after code changes.

Use security-reviewer for trust boundaries.

Review should check tests first:

- Test fails without code.
- Test passes with code.
- Test covers failure path.
- Test name explains behavior.

## Pre-Test Code Enforcement

If code already exists before RED:

```text
Stop.
Delete or revert production change.
Write failing test.
Run test and capture RED.
Re-implement from test.
```

If deleting code is risky, ask user before destructive revert.

If code is in uncommitted user changes, do not delete without confirmation.

If code was generated by prior agent in current task, remove it yourself and restart TDD.

## RED Quality Rules

A valid RED failure:

- Fails because expected behavior is absent.
- Has clear assertion message.
- Runs in project test harness.
- Does not depend on network or clock unless controlled.
- Is deterministic.

Invalid RED failure:

- Syntax error in test.
- Missing dependency from wrong test setup.
- Snapshot mismatch for unrelated output.
- Arbitrary timeout.
- Failure caused by dirty baseline.

## GREEN Quality Rules

A valid GREEN change:

- Makes RED test pass.
- Does not skip, weaken, or delete test.
- Does not add broad fallback hiding failure.
- Does not swallow errors.
- Does not mutate caller-owned data unexpectedly.
- Does not introduce secret, network, or destructive behavior.

## REFACTOR Quality Rules

A valid refactor:

- Keeps same tests green.
- Improves readability or cohesion.
- Removes duplication with same meaning.
- Keeps public contract stable.
- Does not expand scope.

## Verification Checklist

- [ ] Behavior statement written.
- [ ] Test location follows existing convention.
- [ ] Pre-test production code was absent or removed.
- [ ] RED command failed for expected reason.
- [ ] GREEN command passed after minimal implementation.
- [ ] Edge cases added with their own RED/GREEN loops.
- [ ] Refactor ran only after green.
- [ ] Wider validation ran or blocker reported.
- [ ] Code review completed for changed code.
- [ ] Security review completed when trust boundary changed.

## Example Loop

```text
Behavior: skill pack validator rejects missing workflow skill.
Test: tests/test-workflow-pack.js checks required file exists.
RED: node tests/test-workflow-pack.js fails ENOENT.
GREEN: add SKILL.md with required frontmatter.
REFACTOR: tighten required sections.
VALIDATE: npm test passes.
```

## Common Pitfalls

- Writing implementation and test in same step without seeing RED.
- Accepting failure from broken import as RED.
- Adding giant test matrix before first green.
- Refactoring while red.
- Weakening assertion to make test pass.
- Skipping full validation at end.
- Testing implementation detail instead of behavior.
- Keeping prototype code because it seems correct.

## Handoff Output

Strict TDD report:

```text
Behavior:
Test file:
RED command:
RED failure:
GREEN files:
GREEN command:
Refactor:
Wider validation:
Review:
Gaps:
```

Never say "TDD done" without RED and GREEN evidence.
