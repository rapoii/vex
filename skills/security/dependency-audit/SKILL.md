---
    name: dependency-audit
    description: Audit dependencies for vulnerabilities, license risk, stale packages, and supply-chain exposure.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["Dependency update", "Audit failure", "Package selection"]
    ---

    # Dependency Audit

    Audit dependencies for vulnerabilities, license risk, stale packages, and supply-chain exposure.

    ## When to Activate

    - Dependency update
- Audit failure
- Package selection

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/dependency-audit src/api` — apply workflow to specific path.
    - `/dependency-audit failing checkout test` — focus on named issue.
    - `/dependency-audit` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `owasp-top10`
- `secrets-scanning`
- `api-security`
- `auth-hardening`

