---
name: feature-development
description: Workflows for feature development (branching strategy, PR workflow, feature flags).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: workflow
triggers:
  - "how to branch"
  - "feature flag"
  - "pr workflow"
  - "feature-development"
---

# Feature Development

Standardized workflows for creating branches, integrating code, and rolling out features using flags.

## When to Activate
- Task involves starting a new feature branch.
- Configuring LaunchDarkly or custom feature flags.
- Establishing PR templates and review rules.

## How It Works

### Trunk-Based Development
Prefer short-lived feature branches merged directly into `main` (trunk) over long-running release branches (GitFlow).

```bash
# Start a new feature
git checkout main
git pull origin main
git checkout -b feat/add-user-profile

# Commit small, atomic changes
git commit -m "feat: create profile UI component"
git commit -m "feat: wire profile UI to API"
```

### Feature Flags
Use feature flags to decouple deployment from release. This allows merging unfinished code to `main` safely.

```typescript
// Example using a simple feature flag service
import { useFlags } from '@/lib/feature-flags';

export function UserDashboard() {
  const flags = useFlags();

  return (
    <div>
      <h1>Dashboard</h1>
      {/* Code is deployed but hidden from users */}
      {flags.ENABLE_NEW_PROFILE_UI ? (
        <NewProfileView />
      ) : (
        <LegacyProfileView />
      )}
    </div>
  );
}
```

### Pull Request Workflow
1. Keep PRs small (under 400 lines of change).
2. Write a clear description linking to the issue.
3. Require CI checks to pass before merging.
4. Require at least one peer review.

```markdown
# PR Template Example
## What does this PR do?
Implements the new user profile UI hidden behind the `ENABLE_NEW_PROFILE_UI` flag.

## Testing Instructions
1. Turn on flag in admin panel.
2. Navigate to `/profile`.
3. Verify avatar upload works.

## Screenshots
[Insert screenshot]
```

## Verification Steps
1. Verify feature branches live no longer than 2-3 days before merging.
2. Test feature flags by toggling them on/off in the local environment and ensuring the application behaves as expected.
3. Run `git log` to ensure commit messages follow conventional formats.

## Common Pitfalls
- **Feature Flag Debt**: Leaving old feature flags in the code long after 100% rollout. Add a task to remove the flag after the rollout is complete.
- **Merge Conflicts**: Leaving branches open for weeks guarantees massive merge conflicts. Merge early and often using flags.
- **Giant PRs**: Reviewers gloss over PRs larger than 500 lines. Break large features into smaller, reviewable chunks.

## Related Skills
- `deployment-flow`: How to deploy the code once merged.
- `release-workflow`: How to tag and version the `main` branch.

## Pipeline

**Previous:** (feature request) — requested feature or product goal starts development flow
**Next:** [code-review-flow](../code-review-flow/SKILL.md) — review diffs with severity ordering and actionable fixes