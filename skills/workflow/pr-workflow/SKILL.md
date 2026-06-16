---
name: pr-workflow
description: Standardized workflow for reviewing, testing, and creating pull requests.
argument-hint: "[branch | pr-url]"
metadata:
  origin: VEX
  category: workflow
---

# PR Workflow

Actionable steps for creating and reviewing Pull Requests securely and thoroughly.

## When to Activate
- Preparing a branch for a Pull Request.
- Reviewing an open Pull Request.
- Addressing PR feedback.

## Workflow

### 1. Preparation & Self-Review
Before opening a PR, ensure local quality.
```bash
# 1. Update with target branch
git fetch origin main
git rebase origin/main

# 2. Run all local checks
npm run lint
npm run test
npm run build
```

### 2. Crafting the PR
Write a clear, descriptive PR body. Explain the *why*, not just the *what*.

**PR Template Structure:**
```markdown
## Summary
Fixes bug where checkout button was disabled for guest users.

## Changes
- Updated `CheckoutFlow.tsx` to allow null user ID.
- Added `GuestCheckout.test.tsx`.

## Verification Steps
1. Log out.
2. Add item to cart.
3. Click Checkout. Verify modal opens.
```

### 3. Reviewing a PR (Reviewer)
Use a systematic approach to review code.

1. **Understand Intent**: Read the PR description and linked issues.
2. **Review Tests First**: Do the tests accurately reflect the requirements? Are edge cases covered?
3. **Check Architecture**: Does this fit the system design?
4. **Check Security**: Are inputs validated? Are queries parameterized?
5. **Review Implementation**: Look for logic bugs, performance issues, and readability.

### 4. Merging
Prefer Squash and Merge for cleaner history.

```bash
# Example gh CLI command to merge
gh pr merge --squash --delete-branch
```

## Common Pitfalls
- **Massive PRs**: Opening PRs with 1000+ lines of changes. Break them down.
- **Missing Context**: PR descriptions that say "Fixes stuff".
- **Rubber Stamping**: Approving a PR without actually reading the code or running the tests locally.

## Verification Checklist
- [ ] CI/CD pipeline passes.
- [ ] No merge conflicts.
- [ ] All requested changes addressed.
- [ ] Test coverage maintained or improved.

## Pipeline

**Previous:** (pull request need) — branch or PR readiness starts PR flow
**Next:** [code-review-flow](../code-review-flow/SKILL.md) — review diffs with severity ordering and actionable fixes
