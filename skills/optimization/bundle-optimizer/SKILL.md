---
    name: bundle-optimizer
    description: Reduce frontend bundles through code splitting, dependency trimming, lazy loading, and asset hygiene.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Large JS bundle", "Slow load", "Frontend perf work"]
    ---

    # Bundle Optimizer

    Reduce frontend bundles through code splitting, dependency trimming, lazy loading, and asset hygiene.

    ## When to Activate

    - Large JS bundle
- Slow load
- Frontend perf work

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/bundle-optimizer src/api` — apply workflow to specific path.
    - `/bundle-optimizer failing checkout test` — focus on named issue.
    - `/bundle-optimizer` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `token-budget-advisor`
- `model-routing-optimizer`
- `context-window-manager`
- `performance-audit`

