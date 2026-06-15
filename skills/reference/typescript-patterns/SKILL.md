---
    name: typescript-patterns
    description: Use TypeScript types to enforce boundaries, safe narrowing, async correctness, and maintainable APIs.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: reference
      triggers: ["TypeScript API design", "Type errors", "Shared model changes"]
    ---

    # Typescript Patterns

    Use TypeScript types to enforce boundaries, safe narrowing, async correctness, and maintainable APIs.

    ## When to Activate

    - TypeScript API design
- Type errors
- Shared model changes

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/typescript-patterns src/api` — apply workflow to specific path.
    - `/typescript-patterns failing checkout test` — focus on named issue.
    - `/typescript-patterns` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `react-patterns`
- `vue-patterns`
- `django-patterns`
- `fastapi-patterns`

