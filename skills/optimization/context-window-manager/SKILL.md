---
    name: context-window-manager
    description: Keep long sessions effective with summarization, file targeting, memory, and context pruning.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: optimization
      triggers: ["Long task", "Large repo exploration", "Context pressure"]
    ---

    # Context Window Manager

    Keep long sessions effective with summarization, file targeting, memory, and context pruning.

    ## When to Activate

    - Long task
- Large repo exploration
- Context pressure

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/context-window-manager src/api` — apply workflow to specific path.
    - `/context-window-manager failing checkout test` — focus on named issue.
    - `/context-window-manager` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `token-budget-advisor`
- `model-routing-optimizer`
- `performance-audit`
- `bundle-optimizer`

