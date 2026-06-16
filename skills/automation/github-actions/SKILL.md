---
name: github-actions
description: Create and configure GitHub Actions workflows, triggers, matrix jobs, reusable workflows, concurrency limits, and marketplace actions securely.
argument-hint: "[workflow-type | action-target]"
metadata:
  origin: VEX
---

# GitHub Actions

Use this skill when configuring CI/CD pipelines, issue automation, scheduled jobs, or reusable workflows on GitHub.

## Triggers

- User asks for GitHub Actions, `.github/workflows/`, CI for GitHub.
- Setting up automated tests on pull requests.
- Automating releases to npm, PyPI, or GitHub Releases.
- Configuring dependabot, stale issue closers, or cron jobs.
- Fixing action syntax, secret scope, or concurrency limits.

## Inputs To Inspect

- Existing `.github/workflows/*.yml`.
- `package.json` scripts, Makefile, or build tasks.
- Tests to execute in matrix.
- Branch protection requirements.
- Existing environment secrets or variables to map.

## Workflow Setup Strategy

1. Define specific triggers (`push`, `pull_request`, `workflow_dispatch`, `schedule`).
2. Set minimal top-level `permissions` to prevent token abuse.
3. Group related steps into jobs.
4. Use `actions/checkout` and setup actions (`actions/setup-node`, `actions/setup-python`) with caching.
5. Limit concurrency for PR jobs to cancel redundant runs.
6. Use matrix strategies for testing across versions/OS.
7. Use environments for deployments.

## Pull Request Validation

```yaml
name: PR Check

on:
  pull_request:
    branches: [main]

# Cancel in-progress runs for the same PR
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  test:
    name: Test Node ${{ matrix.node }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        node: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test
```

## Release / Publish Workflow

```yaml
name: Publish

on:
  push:
    tags: ['v*']

permissions:
  contents: write    # For GitHub Releases
  id-token: write    # For npm provenance / cloud OIDC

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      
      - name: Publish to npm
        run: npm publish --provenance
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: true
          files: |
            dist/*.zip
            dist/*.tar.gz
```

## Reusable Workflows

Define in one file, call from another to reduce duplication.

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      target_env:
        required: true
        type: string
    secrets:
      API_KEY:
        required: true

jobs:
  run-test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing ${{ inputs.target_env }}"
```

Calling it:

```yaml
# .github/workflows/main.yml
jobs:
  test-staging:
    uses: ./.github/workflows/reusable-test.yml
    with:
      target_env: staging
    secrets:
      API_KEY: ${{ secrets.STAGING_KEY }}
```

## Scheduled Tasks (Cron)

```yaml
on:
  schedule:
    # Run at 02:00 every day
    - cron: '0 2 * * *'
```

## Verification Commands

```bash
# Locally validate action syntax
npx actionlint

# Simulate action run locally with Act (if installed)
act pull_request
```

## Common Pitfalls

- Using `pull_request_target` to checkout untrusted code exposes repository secrets. Use `pull_request` unless explicitly needed for secret access, and NEVER run unreviewed code in `pull_request_target`.
- Using default `GITHUB_TOKEN` permissions grants write access to repos on old organization settings. Always define `permissions:` explicitly.
- Caching dependencies without hashing the lockfile causes build rot.
- Passing unsanitized PR titles/branch names into bash scripts allows command injection (`run: echo "Branch is ${{ github.ref }}"`). Pass as env vars instead.
- Omitting `fail-fast: false` in matrix jobs hides OS-specific failures when an earlier job fails.

## Done Criteria

- Trigger matches intended workflow lifecycle.
- Caching is configured for dependency installs.
- Concurrency limits prevent wasted runner minutes on PRs.
- Least privilege permissions are set at top level.
- Actions use major version tags (`@v4`) not mutable branch names (`@master`).
