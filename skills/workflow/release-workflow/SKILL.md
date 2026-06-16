---
name: release-workflow
description: Workflows for semantic versioning, changelog generation, and hotfixes.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: workflow
triggers:
  - "how to release"
  - "hotfix process"
  - "semantic versioning"
  - "release-workflow"
---

# Release Workflow

Managing software releases, semantic versioning, generating changelogs, and handling critical hotfixes.

## When to Activate
- Task involves cutting a new release.
- Automating changelog generation.
- Fixing a critical bug in production (Hotfix).

## How It Works

### Semantic Versioning (SemVer)
Use `MAJOR.MINOR.PATCH` versioning.
- `MAJOR`: Incompatible API changes.
- `MINOR`: New features in a backward-compatible manner.
- `PATCH`: Backward-compatible bug fixes.

```json
// package.json
{
  "version": "1.4.2" // Patch update from 1.4.1
}
```

### Release Process
Using tools like Release Please or Standard Version automates this process based on Conventional Commits.

1. **Commit**: `feat: add user dashboard`
2. **Release Tool**: Reads commits, determines next version (e.g., MINOR), updates `CHANGELOG.md`, bumps `package.json`.
3. **Tag**: `git tag v1.5.0`
4. **Publish**: Build and deploy the tagged artifact.

### Hotfix Process
When a critical bug hits production, bypass normal feature flow to deploy a fix rapidly.

1. Create a branch from the release tag or `main`.
```bash
git checkout main
git checkout -b hotfix/fix-login-crash
```
2. Write test reproducing bug, then fix.
3. Commit with `fix:` prefix.
4. Merge to `main`.
5. Cut a new PATCH release immediately (e.g., `v1.5.1`).

### Automated Changelog Generation
Require conventional commits (`feat:`, `fix:`, `chore:`) to auto-generate changelogs.

```markdown
# CHANGELOG

## [1.5.0] - 2026-10-15

### Features
* **dashboard**: add user dashboard view (#102)
* **auth**: implement OAuth2 login (#98)

### Bug Fixes
* **profile**: fix avatar upload timeout (#105)
```

## Verification Steps
1. Ensure the `CHANGELOG.md` accurately reflects the changes in the release.
2. Verify the version bump aligns with SemVer rules (no breaking changes in a MINOR release).
3. Ensure CI pipelines trigger the build and deploy steps when a version tag (e.g., `v*`) is pushed.

## Common Pitfalls
- **Manual Version Bumping**: Prone to human error and merge conflicts. Automate versioning based on commit history.
- **Hotfix Divergence**: Creating a hotfix directly on the server or a stray branch and forgetting to backport it to `main`. Always merge hotfixes back to the trunk.
- **Vague Commits**: Commits like "fixed stuff" prevent automated changelog generation. Enforce conventional commits.

## Related Skills
- `feature-development`: How features are built before they are bundled into a release.
- `deployment-flow`: How the released artifact is delivered to servers.