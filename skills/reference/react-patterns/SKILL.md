---
    name: react-patterns
    description: Use modern React component, hook, state, data-fetching, and accessibility patterns.
    argument-hint: "[scope | file | goal]"
    metadata:
      origin: VEX
      category: reference
      triggers: ["React components/hooks", "Client/server state design", "JSX review"]
    ---

    # React Patterns

    Use modern React component, hook, state, data-fetching, and accessibility patterns.

    ## When to Activate

    - React components/hooks
- Client/server state design
- JSX review

    ## How It Works

    1. Clarify scope and success criteria before changing files.
    2. Inspect existing project conventions and reuse local tooling first.
    3. Apply smallest safe change that satisfies requirement.
    4. Validate with targeted commands, tests, or manual checks.
    5. Report result with changed paths, evidence, and remaining risk.

    ## Examples

    - `/react-patterns src/api` — apply workflow to specific path.
    - `/react-patterns failing checkout test` — focus on named issue.
    - `/react-patterns` — infer scope from current diff or task.

    ## Critical Callouts

    - Do not bypass failing quality gates; fix root cause.
    - Prefer project-owned scripts over remote one-off commands.
    - Validate external input, secrets, and shared-state changes carefully.
    - Stop and ask before destructive or externally visible actions.

    ## Related Skills

    - `vue-patterns`
- `django-patterns`
- `fastapi-patterns`
- `docker-patterns`

