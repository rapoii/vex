---
name: worktree-isolation
description: Manage git worktree lifecycle for safe task branches, baseline checks, merge choices, and cleanup.
argument-hint: "[task | branch | scope]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["New implementation branch", "Parallel agent work", "Risky exploratory change", "User asks for worktree isolation"]
---

# Worktree Isolation Workflow

Use this skill when a task should run away from current working tree.

This workflow adapts Superpowers-style git worktree usage for VEX: create isolated workspace, verify clean baseline, work on task branch, then choose merge, PR, keep, or discard.

## When to Activate

- User explicitly asks for worktree.
- Parallel agents will write files.
- Current branch has unrelated work that must remain untouched.
- Task is exploratory and may be discarded.
- Large feature needs clean branch boundary.
- Baseline tests must be proven before edits.
- User wants safe merge or PR choices after completion.

## When Not to Activate

- User asks one small edit in clean working tree.
- Repo is not git and no worktree-compatible adapter exists.
- User only asks for read-only research.
- Task is emergency hotfix on current branch.
- Worktree creation would hide needed uncommitted changes.

## Core Principles

### 1. Isolate Before Editing

Create worktree and branch before changing files.

Do not mix task changes with user's current branch.

Use clear branch name.

### 2. Verify Baseline

Run baseline checks before implementation.

If baseline fails before edits, stop and report.

Do not accept blame for pre-existing failure.

### 3. Keep Lifecycle Explicit

Every worktree ends with one user-visible choice:

- Merge
- Open PR
- Keep for later
- Discard

Never delete dirty worktree without explicit confirmation.

### 4. Avoid Destructive Git Shortcuts

Do not run reset hard, clean force, branch delete, or force push unless user explicitly asks.

Prefer safe status, diff, and normal merge flow.

### 5. Preserve Evidence

Record branch, worktree path, baseline result, validation result, and final choice.

## Workflow

### Step 1: Preflight Current Repo

Check:

```bash
git status --short
git branch --show-current
git remote -v
```

If uncommitted changes exist, explain they remain in original worktree.

If task depends on those changes, ask user whether to base worktree on current HEAD or include patch.

### Step 2: Choose Branch Name

Use lowercase slash name.

Examples:

```text
feat/workflow-brainstorming
fix/hook-path-guard
docs/worktree-isolation
```

Branch name should encode task, not ticket system unless user requested.

Avoid spaces and uppercase.

### Step 3: Create Worktree

Preferred pattern:

```bash
git worktree add .claude/worktrees/<task-slug> -b <branch-name>
```

If project harness provides worktree tool, use it when user asked for tool-managed worktree.

Do not create worktree outside repo-controlled or user-approved location.

### Step 4: Enter Worktree

Confirm location.

Run:

```bash
git status --short
git branch --show-current
```

Ensure branch matches expected task branch.

### Step 5: Install Or Reuse Dependencies

If dependencies are absent, use project install command only with user approval when it changes lockfiles or downloads packages.

Prefer existing dependencies.

Do not add paid-service dependency to required path.

### Step 6: Verify Clean Baseline

Run narrow baseline first.

Examples:

```bash
npm test
pytest -q
go test ./...
python tools/vex.py doctor --json
```

Pick command from project docs or package scripts.

Record result.

If baseline fails:

- Stop implementation.
- Report command and failure.
- Ask whether to fix baseline or continue knowingly.

### Step 7: Execute Task

Use approved plan.

Keep changes scoped.

Run TDD if behavior changes.

For parallel agents, ensure each worktree edits independent files or branches.

### Step 8: Validate In Worktree

Run targeted tests first.

Then run full validation if task scope justifies.

Record exact commands.

Do not claim feature works without validation.

### Step 9: Review Diff

Run:

```bash
git status --short
git diff
```

Check for:

- Unrelated files
- Generated caches
- Secrets
- Lockfile drift
- Large accidental changes
- Test artifacts

Use code-reviewer after edits.

Use security-reviewer for filesystem, hooks, installers, network, secrets, auth, subprocesses.

### Step 10: Present Completion Options

After validation and review, present options:

```text
1. Merge into original branch.
2. Push branch and create PR.
3. Keep worktree for later.
4. Discard worktree and branch.
```

Explain state:

- Worktree path
- Branch name
- Validation status
- Dirty or clean
- Commits ahead if any

Ask user before shared or destructive actions.

### Step 11: Merge Option

Before merge:

```bash
git status --short
git checkout <original-branch>
git merge <branch-name>
```

Only merge when:

- Tests passed.
- Review passed.
- User approved merge.
- Original branch state is understood.

If conflict occurs, stop and resolve deliberately.

Do not abort or reset without confirmation.

### Step 12: PR Option

Before PR:

```bash
git status --short
git log --oneline <base>..HEAD
git diff <base>...HEAD
```

Push only after user asked.

Create PR with summary, tests, and risk.

### Step 13: Keep Option

Leave worktree intact.

Report:

```text
Worktree kept: <path>
Branch: <branch>
Resume command: <how to enter>
```

Do not cleanup.

### Step 14: Discard Option

Discard is destructive.

Require explicit user confirmation if:

- Worktree has uncommitted changes.
- Branch has commits not merged.
- User might lose work.

Safe cleanup after confirmation:

```bash
git worktree remove <path>
git branch -d <branch-name>
```

Use force deletion only when user explicitly confirms loss.

## Baseline Failure Policy

Baseline failure means repo was not clean before task.

Stop unless user explicitly approves continuing.

Report:

```text
Baseline failed before edits.
Command: <command>
Failure: <short output>
No task changes made.
Options: fix baseline, choose narrower command, continue with known failure.
```

## Parallel Agent Worktrees

For each independent task:

- Create separate worktree.
- Use unique branch.
- Restrict file scope.
- Run task validation in that worktree.
- Merge one branch at a time.

Never let multiple worktrees auto-merge into same branch without review.

## Naming Conventions

Worktree path:

```text
.claude/worktrees/<task-slug>
```

Branch:

```text
<type>/<task-slug>
```

Types:

- feat
- fix
- docs
- test
- refactor
- chore
- security

## Safety Rules

- Ask before deleting worktree with changes.
- Ask before branch deletion with unmerged commits.
- Ask before push or PR.
- Never force push main or master.
- Never run broad cleanup to hide conflicts.
- Do not copy secrets into worktree reports.
- Treat git hooks as active and do not bypass them.

## Verification Checklist

- [ ] Current branch and status checked before worktree.
- [ ] Branch name is task-scoped.
- [ ] Worktree path is known and safe.
- [ ] Baseline command ran before edits.
- [ ] Baseline result recorded.
- [ ] Task validation ran after edits.
- [ ] Diff reviewed for unrelated changes.
- [ ] Code review completed when files changed.
- [ ] Security review completed when triggered.
- [ ] User selected merge, PR, keep, or discard.
- [ ] Cleanup used safe git commands only after approval.

## Example Lifecycle

```text
Task: Add strict TDD workflow skill.
Branch: docs/strict-tdd-workflow
Worktree: .claude/worktrees/strict-tdd-workflow
Baseline: npm test passed before edits.
Implementation: added SKILL.md and tests.
Validation: npm test passed after edits.
Review: code-reviewer approved docs contract.
Decision: keep worktree for PR.
```

## Common Pitfalls

- Creating branch after edits already happened.
- Skipping baseline and misdiagnosing old failures.
- Running full cleanup while user changes are present.
- Forgetting to return to original branch before merge.
- Auto-deleting worktree with uncommitted changes.
- Running parallel agents against same files.
- Treating worktree isolation as permission to ignore tests.

## Handoff Output

Final handoff:

```text
Worktree:
Branch:
Baseline:
Validation:
Review:
Diff summary:
Recommended option:
Needs user decision:
```

Do not hide dirty status.

Do not call task complete until user-selected lifecycle action is clear.
