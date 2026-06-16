---
name: multi-frontend
description: Frontend-focused multi-model workflow for UI, state, accessibility, and UX.
argument-hint: "[screen | component | user flow | blank for current diff]"
---

# Multi Frontend

**Input**: $ARGUMENTS

## Purpose

Coordinate frontend work across component structure, state, accessibility, and manual verification.
Use this for UI changes, flows, design-system updates, and browser-visible behavior.
Prefer user-visible proof over type checks alone.

## Workflow

1. Use Sonnet to map components, routes, state, and styling patterns.
2. Use accessibility agent for keyboard, ARIA, labels, and contrast.
3. Use Sonnet to implement component and test changes.
4. Use Opus if state architecture or UX tradeoff is contested.
5. Start app and exercise golden path in browser when possible.
6. Check edge cases: empty, loading, error, long text, narrow viewport.
7. Run lint, typecheck, and focused frontend tests.
8. Review final UI diff for unnecessary abstraction.

## Model Selection

- Sonnet: component edits, tests, state updates, CSS pattern matching.
- Opus: major UX/state decisions and cross-page architecture.
- Haiku: component inventory, route lists, simple copy updates.

## Rationale

Frontend work needs quick iteration plus real interaction checks.
Use Opus when model choice affects long-term component boundaries.
Use specialist accessibility review for WCAG-sensitive behavior.

## Guardrails

- Do not claim UI success without running or explaining why not.
- Preserve keyboard navigation and visible focus.
- Avoid speculative component abstractions.
- Keep generated output reproducible.

## Output

- User flow verified or reason not verified.
- Accessibility checks performed.
- Tests and browser evidence.
