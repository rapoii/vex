---
    name: owasp-top10
    description: Check app code against OWASP Top 10 with concrete mitigation patterns.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["Security review", "User input/API/auth changes", "Pre-release audit"]
    ---

    # Owasp Top10

    Check app code against OWASP Top 10 with concrete mitigation patterns.

    ## When to Activate

    - Security review
- User input/API/auth changes
- Pre-release audit

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/owasp-top10 src/api` — apply workflow to specific path.
    - `/owasp-top10 failing checkout test` — focus on named issue.
    - `/owasp-top10` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `dependency-audit`
- `secrets-scanning`
- `api-security`
- `auth-hardening`

