---
    name: model-routing-optimizer
    description: Route tasks to appropriate models by complexity, latency, cost, and risk.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Agent design", "Cost optimization", "Model choice"]
    ---

    # Model Routing Optimizer

    Route tasks to appropriate models by complexity, latency, cost, and risk.

    ## When to Activate

    - Agent design
- Cost optimization
- Model choice

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/model-routing-optimizer src/api` — apply workflow to specific path.
    - `/model-routing-optimizer failing checkout test` — focus on named issue.
    - `/model-routing-optimizer` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `token-budget-advisor`
- `context-window-manager`
- `performance-audit`
- `bundle-optimizer`

