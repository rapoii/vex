---
    name: vue-patterns
    description: Use Vue 3 Composition API, reactivity, routing, Pinia, and SFC patterns.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: reference
      triggers: ["Vue SFC work", "Composition API design", "Pinia/router changes"]
    ---

    # Vue Patterns

    Use Vue 3 Composition API, reactivity, routing, Pinia, and SFC patterns.

    ## When to Activate

    - Vue SFC work
- Composition API design
- Pinia/router changes

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/vue-patterns src/api` — apply workflow to specific path.
    - `/vue-patterns failing checkout test` — focus on named issue.
    - `/vue-patterns` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `react-patterns`
- `django-patterns`
- `fastapi-patterns`
- `docker-patterns`

