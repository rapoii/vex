---
    name: token-budget-advisor
    description: Estimate token cost, context pressure, and agent fan-out before large LLM tasks.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Large prompt/workflow", "Many agents", "Cost-sensitive run"]
    ---

    # Token Budget Advisor

    Estimate token cost, context pressure, and agent fan-out before large LLM tasks.

    ## When to Activate

    - Large prompt/workflow
- Many agents
- Cost-sensitive run

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/token-budget-advisor src/api` — apply workflow to specific path.
    - `/token-budget-advisor failing checkout test` — focus on named issue.
    - `/token-budget-advisor` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `model-routing-optimizer`
- `context-window-manager`
- `performance-audit`
- `bundle-optimizer`

