---
name: finishing-development-branch
description: Finish a development branch with verification, review, and explicit cleanup choices.
argument-hint: "[branch | worktree | pr]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["Work complete on branch", "Worktree cleanup", "Before merge", "Before PR"]
---

# Finishing Development Branch

Use this workflow after implementation work is done on a branch or worktree.

This adapts Superpowers branch-finishing discipline for VEX: verify work, summarize state, present safe options, and never merge, delete, or discard without explicit user choice.

## When to Activate

- Feature branch appears complete.
- Worktree task batch is finished.
- User asks what remains before merge.
- User asks to finish or clean up a branch.
- User asks to create a PR after local work.
- Subagent worktree result needs integration.
- Local diff has been reviewed and verified.
- Branch has commits that need disposition.
- User asks to discard experimental work.

## When Not to Activate

- Work is still failing required validation.
- Requirements are unresolved.
- Branch has merge conflicts that need implementation work first.
- User only asked for a status summary.
- Current directory is not a git repository and no worktree manager exists.
- The branch contains unknown user changes you have not inspected.

## Core Rule

Branch finishing is a decision point.

Do not assume desired outcome.

Always present options:

1. Merge to main.
2. Create pull request.
3. Keep branch.
4. Discard branch or worktree.

Each option has different blast radius.

## Workflow

### Step 1: Capture Current State

Check branch state before any finishing action.

Required facts:

- Current branch name
- Base branch
- Uncommitted changes
- Untracked files
- Commits ahead or behind
- Remote tracking status
- Worktree path if applicable
- Test status
- Review status

Use safe git commands only.

Do not reset, clean, delete, merge, or checkout away until user chooses.

### Step 2: Inspect Changes

Understand what branch contains.

Look at:

- `git status`
- `git diff`
- `git diff --cached`
- `git log --oneline <base>..HEAD`
- `git diff <base>...HEAD`

Identify files changed, purpose, and risk.

Do not include secrets or credential files in final branch action.

### Step 3: Verify All Tests Pass

Run required validation before presenting merge or PR as ready.

Typical checks:

```bash
npm test
npm run build
npm run lint
node tests/test-workflow-pack.js
```

Use project-specific commands when known.

If validation is too expensive, say what was not run and why.

### Step 4: Run Review Gates

Before finalizing:

- Use code-reviewer for correctness and maintainability.
- Use security-reviewer for hooks, installers, file writes, external calls, secrets, auth-like flows, subprocesses, or CI changes.
- Use domain reviewer when branch touches specialized area.
- Fix blocking findings before merge or PR.

Non-critical findings may be deferred only if user accepts.

### Step 5: Prepare Summary

Summarize branch state:

```text
Branch:
Base:
Commits:
Files changed:
Tests:
Reviews:
Known risks:
Uncommitted changes:
```

Keep summary factual.

Do not imply merge approval if checks failed.

### Step 6: Present Options

Offer explicit choices.

#### Option A: Merge to Main

Use when work is local, verified, reviewed, and user wants direct integration.

Before merge:

- Confirm target branch.
- Confirm working tree clean or intended changes committed.
- Confirm tests passed.
- Confirm branch is up to date enough for safe merge.
- Confirm user wants merge now.

After merge:

- Switch to target branch.
- Merge cleanly.
- Run smoke validation if needed.
- Delete local branch only after successful merge and user-approved cleanup.
- Remove worktree only after preserving needed commits.

Never force merge unresolved conflicts.

#### Option B: Create Pull Request

Use when work should be reviewed by others or CI.

Before PR:

- Confirm remote branch exists or push is authorized.
- Draft title under 70 characters.
- Draft summary with motivation, changes, tests, risks.
- Include verification evidence.
- Do not push without explicit approval.

PR body should include:

```markdown
## Summary
- ...

## Test plan
- ...

## Risks
- ...
```

After PR:

- Return PR URL.
- Mention any CI or review follow-up.

#### Option C: Keep Branch

Use when work should remain available but not merged.

Document state:

- Branch name
- Worktree path
- Latest commit
- Uncommitted changes
- Tests run
- Next step
- Known blockers

If worktree exists, tell user how to re-enter it.

Do not delete anything.

#### Option D: Discard Branch or Worktree

Use when user wants to abandon work.

Discard is destructive.

Before discard:

- Show exactly what will be lost.
- Confirm branch/worktree name.
- Confirm uncommitted files.
- Confirm commits not on base.
- Ask explicit confirmation.

Only after confirmation:

- Remove worktree if applicable.
- Delete branch if safe and requested.
- Do not delete remote branch unless user explicitly asks.

### Step 7: Execute Chosen Option

Execute only chosen path.

Do not combine actions silently.

For example, creating PR does not imply deleting local branch.

Merging does not imply pushing.

Keeping branch does not imply stashing.

Discarding worktree does not imply deleting remote branch.

### Step 8: Verify Final State

After chosen action, verify final state.

For merge:

- Target branch contains commits.
- Source branch removed only if intended.
- Worktree clean.

For PR:

- PR URL exists.
- Remote branch contains commits.
- PR body matches summary.

For keep:

- Branch/worktree still exists.
- User has re-entry instructions.

For discard:

- Worktree/branch removed as confirmed.
- Base branch unaffected.

## Verification Checklist

- [ ] Current branch identified.
- [ ] Base branch identified.
- [ ] Uncommitted and untracked files inspected.
- [ ] Commits ahead of base inspected.
- [ ] Full branch diff understood.
- [ ] Tests/build/lint ran or skipped with reason.
- [ ] Code review completed.
- [ ] Security review completed when needed.
- [ ] Blocking findings resolved.
- [ ] Options presented: merge, PR, keep, discard.
- [ ] User selected one option.
- [ ] Destructive action confirmed explicitly.
- [ ] Final state verified.

## Superpowers Discipline

Superpowers branch finishing treats the end of a task as controlled handoff.

Useful habits:

- Finish with evidence, not optimism.
- Separate verification from disposition.
- Keep human in control of irreversible choices.
- Preserve useful work unless discard is explicit.
- Make next action obvious.

A branch is not finished because code was written.

It is finished when state is known, checks pass, review is resolved, and user chooses what happens next.

## Failure Handling

If tests fail:

- Do not present merge as ready.
- Report failing command.
- Offer fix, keep branch, or stop.

If branch has unknown changes:

- Stop.
- Ask user whether they own them.
- Do not overwrite or stash automatically.

If merge conflicts occur:

- Stop and report conflicted files.
- Resolve only with user approval or clear scope.
- Re-run validation after resolution.

If PR creation fails:

- Report exact failure.
- Do not retry with force or bypass.
- Check auth, remote, and branch tracking.

## Output Format

Before choice:

```text
Branch status:
Verification:
Review:
Changed files:
Risks:
Options:
1. Merge to <target>
2. Create PR
3. Keep branch
4. Discard branch/worktree
Decision needed:
```

After action:

```text
Action taken:
Final state:
Verification:
Next step:
```

## Anti-Patterns

- Auto-merging because tests passed.
- Deleting branch immediately after PR.
- Discarding uncommitted work to clean status.
- Hiding failing tests behind "mostly done".
- Creating PR without explaining risks.
- Force pushing as cleanup.
- Removing worktree with unmerged commits without confirmation.
- Assuming main branch name.
- Skipping review because change is docs-only.

## VEX-Specific Notes

For VEX:

- Use code-reviewer after docs or code changes.
- Use security-reviewer for hooks, installers, external calls, file writes, secrets, auth-like flows.
- Keep generated files reproducible.
- Avoid destructive install behavior.
- Do not add telemetry or paid-service dependencies.
- Respect MIT/free-forever constraints.
