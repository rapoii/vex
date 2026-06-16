---
name: release-automation
description: Automate semantic versioning, changelog generation, GitHub releases, and package publishing (npm, PyPI) to eliminate manual deployment errors.
argument-hint: "[package-manager | workflow-file | version-bump]"
metadata:
  origin: VEX
---

# Release Automation

Use this skill when setting up tools to bump versions, generate changelogs from commits, create tags, and publish packages automatically.

## Triggers

- User asks to automate releases, semantic release, release-please, or standard-version.
- Need to publish to npm, PyPI, or crates.io automatically on merge.
- Setting up changelog generation based on conventional commits.
- Moving from manual tags to automated release pipelines.

## Inputs To Inspect

- `package.json`, `pyproject.toml`, or `Cargo.toml` for current versioning strategy.
- Git commit history to verify conventional commit usage.
- `.github/workflows/` or `.gitlab-ci.yml` for existing publish jobs.
- Target registries and required provenance/authentication.

## Automation Strategy

1. Require Conventional Commits (`feat:`, `fix:`, `BREAKING CHANGE:`) so tools can determine the next semantic version.
2. Choose an automation tool: `semantic-release` (fully automated on push) or `release-please` (PR-based approval).
3. Authenticate with package registries using OIDC (provenance) or scoped tokens.
4. Run tests and builds before the publish step.
5. Create a GitHub/GitLab release with the generated changelog attached.

## Semantic Release (Node/npm Baseline)

`semantic-release` runs on CI after a merge to the default branch. It reads commits, bumps `package.json`, creates a Git tag, publishes to npm, and creates a GitHub Release.

Configure `.releaserc` or `package.json`:

```json
{
  "release": {
    "branches": ["main"],
    "plugins": [
      "@semantic-release/commit-analyzer",
      "@semantic-release/release-notes-generator",
      "@semantic-release/npm",
      "@semantic-release/github"
    ]
  }
}
```

GitHub Action (`.github/workflows/release.yml`):

```yaml
name: Release
on:
  push:
    branches: [main]
permissions:
  contents: write # for github releases
  id-token: write # for npm provenance
jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
        run: npx semantic-release
```

## Release Please (Google's PR-based approach)

`release-please` opens a "Release PR" that updates the changelog and version. Merging that PR triggers the actual publish.

GitHub Action (`.github/workflows/release-please.yml`):

```yaml
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: google-github-actions/release-please-action@v4
        id: release
        with:
          release-type: node
      
      # The steps below only run when the release PR is merged
      - uses: actions/checkout@v4
        if: ${{ steps.release.outputs.release_created }}
      - uses: actions/setup-node@v4
        if: ${{ steps.release.outputs.release_created }}
        with:
          node-version: 22
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
        if: ${{ steps.release.outputs.release_created }}
      - run: npm run build
        if: ${{ steps.release.outputs.release_created }}
      - run: npm publish --provenance
        if: ${{ steps.release.outputs.release_created }}
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Local Fallback (Changesets)

For monorepos or projects preferring manual version intent:

1. Install: `npm i -D @changesets/cli`
2. Init: `npx changeset init`
3. Dev workflow: Run `npx changeset` to create a markdown intent file.
4. Release workflow: `npx changeset version` (bumps files), then `npx changeset publish`.

## Verification Commands

```bash
# Semantic release dry-run to see what would happen
npx semantic-release --dry-run
```

## Common Pitfalls

- Publishing without running tests/builds first.
- Failing to use Conventional Commits, resulting in no releases being triggered.
- Missing `GITHUB_TOKEN` write permissions, causing tag creation to fail.
- Hardcoding versions in multiple places instead of letting the tool manage them.
- Triggering publish workflows on forks.

## Done Criteria

- Merging a `feat:` commit automatically bumps the minor version.
- Merging a `fix:` commit automatically bumps the patch version.
- Changelog is generated with links to commits and PRs.
- Artifacts are pushed to the target registry automatically.
