---
    name: auth-hardening
    description: Harden sessions, tokens, password flows, MFA, cookies, and authorization checks.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["Auth code", "Session/token changes", "Privilege boundaries"]
    ---

    # Auth Hardening

    Harden sessions, tokens, password flows, MFA, cookies, and authorization checks.

    ## When to Activate

    - Auth code
- Session/token changes
- Privilege boundaries

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/auth-hardening src/api` — apply workflow to specific path.
    - `/auth-hardening failing checkout test` — focus on named issue.
    - `/auth-hardening` — infer scope from current diff or task.

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

