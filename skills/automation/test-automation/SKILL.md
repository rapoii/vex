---
    name: test-automation
    description: Automate unit, integration, E2E, coverage, and flake detection in local and CI flows.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: automation
      triggers: ["Testing pipeline", "Coverage gap", "Flaky tests"]
    ---

    # Test Automation

    Automate unit, integration, E2E, coverage, and flake detection in local and CI flows.

    ## When to Activate

    - Testing pipeline
- Coverage gap
- Flaky tests

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/test-automation src/api` — apply workflow to specific path.
    - `/test-automation failing checkout test` — focus on named issue.
    - `/test-automation` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `ci-cd-setup`
- `github-actions`
- `docker-compose`
- `pre-commit-hooks`

