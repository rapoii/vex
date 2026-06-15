---
    name: api-security
    description: Secure APIs with authn/z, validation, rate limits, error hygiene, CORS, and logging.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["API endpoint work", "Public API exposure", "Auth middleware"]
    ---

    # Api Security

    Secure APIs with authn/z, validation, rate limits, error hygiene, CORS, and logging.

    ## When to Activate

    - API endpoint work
- Public API exposure
- Auth middleware

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/api-security src/api` — apply workflow to specific path.
    - `/api-security failing checkout test` — focus on named issue.
    - `/api-security` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `owasp-top10`
- `dependency-audit`
- `secrets-scanning`
- `auth-hardening`

