---
    name: secrets-scanning
    description: Find and prevent committed secrets with scanners, allowlists, rotation guidance, and CI gates.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: security
      triggers: ["Before commit", "Security incident", "Repo publication"]
    ---

    # Secrets Scanning

    Find and prevent committed secrets with scanners, allowlists, rotation guidance, and CI gates.

    ## When to Activate

    - Before commit
- Security incident
- Repo publication

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/secrets-scanning src/api` — apply workflow to specific path.
    - `/secrets-scanning failing checkout test` — focus on named issue.
    - `/secrets-scanning` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `owasp-top10`
- `dependency-audit`
- `api-security`
- `auth-hardening`

