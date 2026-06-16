---
name: subagent-development
description: Execute approved plans through fresh subagents, two-stage review, batching, and human checkpoints.
argument-hint: "[plan | task list | scope]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["Approved implementation plan", "Multiple independent tasks", "Long-running agentic build", "User requests subagents"]
---

# Subagent Development Workflow

Use this skill after a spec and plan exist.

This workflow adapts Superpowers-style subagent-driven development for VEX: one fresh subagent per task, isolated context, two-stage review, parallel independent work, and human checkpoints between batches.

## When to Activate

- Approved plan contains multiple implementation tasks.
- Tasks can be split into independent units.
- User wants ECC agents used during build.
- Context pollution could hurt later reasoning.
- Work needs repeated implementation and review loops.
- Human should inspect progress at safe checkpoints.
- Task list is clear enough for subagents to execute without inventing scope.

## When Not to Activate

- Task is one obvious edit.
- Plan is not approved or acceptance criteria are unclear.
- Tasks all edit same files and cannot be isolated.
- User asked for direct pair-programming in main session.
- Security-sensitive task lacks authorization or review plan.
- Build state is already broken and needs triage first.

## Core Principles

### 1. Fresh Context Per Task

Each implementation task gets a new subagent.

The subagent receives only needed spec, files, constraints, and validation command.

Do not rely on prior subagent memory.

Do not ask one subagent to infer global plan from conversation history it cannot see.

### 2. Small Task Units

A good subagent task has:

- One goal
- Named files or search target
- Clear success criteria
- Clear non-goals
- Validation command
- Expected report shape

If task cannot be explained in one prompt, split it.

### 3. Parallel Only When Independent

Run tasks in parallel only when they do not edit same files or depend on each other.

Independent examples:

- One agent writes docs while another writes tests for different validator.
- One agent reviews security while another reviews code quality.
- One agent inspects skills while another inspects agents.

Dependent examples must be sequential:

- Tests before implementation.
- Shared manifest before generated docs.
- API contract before client code.

### 4. Two-Stage Review

Every implementation result gets two checks:

1. Spec compliance review
2. Code quality review

Spec compliance asks: did subagent build what plan requested?

Code quality asks: is implementation maintainable, safe, simple, and tested?

A task passes only when both reviews have no blocking findings.

### 5. Batch With Human Checkpoints

Execute several safe tasks, then stop.

Show changed files, tests run, review results, and next batch.

Ask user before risky next batch.

Never disappear for hours without progress evidence when shared state or destructive options are involved.

## Workflow

### Step 1: Confirm Inputs

Required inputs:

- Approved spec
- Ordered plan or task list
- Acceptance criteria
- Repo path
- Test commands
- Risk notes
- Human checkpoint policy

If any missing, return to brainstorming or planning.

### Step 2: Normalize Task List

Turn plan into task cards.

Task card format:

```text
Task ID:
Goal:
Files allowed:
Files forbidden:
Inputs:
Acceptance criteria:
Validation:
Risk level:
Dependencies:
Expected report:
```

Do not include secrets or unrelated context.

Do not include broad write access when one file is enough.

### Step 3: Classify Dependencies

Mark each task:

- Independent
- Depends on tests
- Depends on contract
- Depends on prior generated file
- Review-only
- Human-decision blocked

Build a dependency graph.

Use parallel execution only within same independent layer.

### Step 4: Choose Isolation Mode

Use same working tree for sequential tasks that edit same files.

Use worktree isolation when parallel agents may write files.

Use read-only agents for review.

Do not let parallel agents edit same file in same worktree.

### Step 5: Spawn Fresh Implementation Agents

Each subagent prompt must be self-contained.

Prompt template:

```text
You are implementing Task <id> for VEX.
Goal: <goal>
Context: <brief spec excerpt>
Allowed files: <paths>
Do not edit: <paths>
Acceptance criteria: <criteria>
Validation command: <command>
Report: files changed, tests run, result, blockers.
```

If task writes code, include TDD requirement.

If task writes docs, include exact content contract.

If task touches filesystem, subprocess, hooks, network, or secrets, include security constraints.

### Step 6: Collect Results

For each subagent, capture:

- Files changed
- Tests run
- Test output summary
- Known gaps
- Assumptions made
- Suggested follow-up

Do not trust summary blindly.

Inspect diff before reporting success.

### Step 7: Stage One Review: Spec Compliance

Use reviewer agent or main session.

Check against task card.

Questions:

- Did task change only allowed files?
- Did output satisfy each acceptance criterion?
- Did it avoid non-goals?
- Did it preserve required style and metadata?
- Did validation actually run?
- Did it invent features?

Findings format:

```text
[BLOCKER] Task 2 missed acceptance criterion X.
Evidence: <file:line or test output>
Fix: <specific change>
```

Blocking spec issues go back to implementation agent or main session fix.

### Step 8: Stage Two Review: Code Quality

Use code-reviewer after spec compliance.

Also use language reviewer for language code.

Use security-reviewer for trust boundaries.

Check:

- Simplicity
- File size
- Error handling
- Input validation
- Tests
- No debug leftovers
- No hardcoded secrets
- No speculative abstractions

Do not debate style covered by formatter.

### Step 9: Merge Results

For same worktree execution, merge means keep edits after review.

For isolated worktrees, merge by normal git flow or apply patch after review.

Before merge:

- Ensure tests pass in integration worktree.
- Check git diff.
- Resolve conflicts manually.
- Reject unrelated changes.

Never force merge dirty or failing work.

### Step 10: Run Batch Validation

After a batch, run targeted validation.

Examples:

```bash
npm test
python -m pytest tests/test_install.py -q
npm run skill:list
```

Use smallest meaningful command first.

Run full validation before final completion.

### Step 11: Human Checkpoint

Report:

```text
Batch complete.
Tasks done: <ids>
Files changed: <paths>
Validation: <commands and pass/fail>
Review: <blocking findings or none>
Next batch: <ids>
Decision needed: <yes/no>
```

Ask user only when checkpoint requires choice.

Proceed autonomously only inside approved safe batch.

### Step 12: Continue Or Stop

Continue if:

- Current batch passes validation.
- No blocking review findings remain.
- Next tasks are within approved scope.
- No new user decision needed.

Stop if:

- Tests fail unexpectedly.
- Review finds critical/high issue.
- Task requires destructive action.
- Spec ambiguity appears.
- Parallel changes conflict.

## Two-Stage Review Details

### Spec Compliance Review

Spec compliance reviewer should be strict.

It does not judge architecture taste.

It compares result to plan.

Evidence sources:

- Diff
- Tests
- File paths
- Acceptance criteria
- Non-goals

Approval requires all acceptance criteria met or explicitly deferred by user.

### Code Quality Review

Quality reviewer checks implementation.

It should find bugs, unsafe handling, and unnecessary complexity.

Approval requires no CRITICAL or HIGH issues.

MEDIUM issues may become follow-up only if they do not affect correctness.

### Review Separation

Do not combine both review stages in one prompt unless task is trivial.

Spec compliance catches wrong solution.

Quality review catches bad solution.

Both matter.

## Parallel Batch Rules

Allowed parallel work:

- Read-only exploration across different subsystems.
- Independent docs under different directories.
- Independent tests for different modules.
- Multiple reviewers on same diff.
- Implementation agents in separate worktrees with non-overlapping files.

Forbidden parallel work:

- Two agents editing same file.
- One agent editing tests while another edits code for same behavior without coordination.
- Multiple agents changing package metadata.
- Parallel destructive git operations.
- Parallel migrations that depend on order.

## Human Checkpoint Rules

Checkpoint before:

- Starting implementation after plan.
- Merging isolated worktree output.
- Running destructive cleanup.
- Pushing branch or creating PR.
- Broad refactor batch.
- Security-sensitive change.

Checkpoint after:

- Batch validation completes.
- Review returns blocking finding.
- Test baseline fails.
- Scope changes.

## Report Contract For Subagents

Each subagent final report must include:

```text
Task:
Files changed:
Acceptance criteria status:
Tests run:
Result:
Blockers:
Notes:
```

If no files changed, say why.

If tests were not run, say why and do not claim success.

## Failure Handling

### Subagent Fails To Finish

Read report or transcript summary.

Classify failure:

- Missing context
- Bad task split
- Test failure
- Build failure
- Permission issue
- Spec ambiguity

Fix task card before retry.

### Review Finds Spec Miss

Send focused correction.

Do not ask same agent to re-read whole plan.

Prompt with exact missed criterion and allowed files.

### Review Finds Quality Issue

Fix in main session or spawn repair agent.

Run same validation again.

Request second review for blocking findings.

### Merge Conflict

Stop automatic batch.

Inspect conflict.

Prefer smaller patch or manual integration.

Ask user if conflict implies product decision.

## Safety Rules

- No subagent receives secrets unless explicitly authorized.
- No subagent runs destructive git commands without user confirmation.
- No subagent edits outside allowed scope.
- No subagent pushes, comments, or posts externally unless user requested.
- Treat subagent output as claims until verified.
- Use security-reviewer for filesystem writes, hooks, installers, network calls, auth, secrets, and subprocesses.

## Verification Checklist

- [ ] Plan exists and is approved.
- [ ] Task cards are independent or ordered by dependency.
- [ ] Fresh subagent prompt is self-contained.
- [ ] Parallel tasks do not edit same files.
- [ ] Each implementation has spec compliance review.
- [ ] Each implementation has code quality review.
- [ ] Security review ran when trust boundaries changed.
- [ ] Targeted tests ran after each batch.
- [ ] Final validation ran before completion.
- [ ] User checkpoint occurred before risky actions.

## Example Batch

```text
Batch 1:
- Task A: Add failing tests for workflow pack contract.
- Task B: Draft brainstorming skill.
- Task C: Draft brainstormer agent.

Parallelism:
- B and C can run in separate worktrees after A defines contract.
- A must complete first because it sets validation.

Reviews:
- Spec compliance checks line counts and required sections.
- Code quality checks clarity, metadata, and no unsafe workflow instructions.
```

## Common Pitfalls

- Spawning one giant agent for whole project.
- Giving subagent vague prompt and hoping it infers intent.
- Running implementation and review in same context without skepticism.
- Treating subagent report as proof.
- Parallelizing conflicting edits.
- Skipping human checkpoint after failed tests.
- Letting repair work drift beyond task card.
- Forgetting security review for file operations.

## Completion Output

Final output after all batches:

```text
Implemented:
- <task summary>

Validation:
- <command>: pass

Reviews:
- Spec compliance: pass
- Code quality: pass
- Security: pass or not triggered

Remaining:
- <none or follow-up>
```

Do not claim completion when validation or review failed.
