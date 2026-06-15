---
    name: supply-chain-review
    description: Review build chain, packages, actions, containers, and publishing for supply-chain risk.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["New external dependency", "CI/action changes", "Publishing package"]
    ---

    # Supply Chain Review

    Review build chain, packages, actions, containers, and publishing for supply-chain risk.

    ## When to Activate

    - New external dependency
- CI/action changes
- Publishing package

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/supply-chain-review src/api` — apply workflow to specific path.
    - `/supply-chain-review failing checkout test` — focus on named issue.
    - `/supply-chain-review` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `owasp-top10`
- `dependency-audit`
- `secrets-scanning`
- `api-security`

