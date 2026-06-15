---
    name: ci-cd-setup
    description: Create CI/CD pipelines with deterministic installs, caching, quality gates, artifacts, and deploy controls.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: automation
      triggers: ["New CI pipeline", "Broken CI", "Release automation"]
    ---

    # Ci Cd Setup

    Create CI/CD pipelines with deterministic installs, caching, quality gates, artifacts, and deploy controls.

    ## When to Activate

    - New CI pipeline
- Broken CI
- Release automation

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/ci-cd-setup src/api` — apply workflow to specific path.
    - `/ci-cd-setup failing checkout test` — focus on named issue.
    - `/ci-cd-setup` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `github-actions`
- `docker-compose`
- `pre-commit-hooks`
- `release-automation`

