# Claude Code Instructions for VEX

VEX is Vareva ECC Extended: a free MIT-licensed agent harness system. Build it as a real reusable tool, not a demo.

## Priorities

1. Claude Code support first.
2. Cross-harness abstractions second.
3. Dashboard and advanced automation after core packs work.

## Required workflow

- Plan before complex changes.
- Use TDD for behavior, validators, installers, and generators.
- Use code review after edits.
- Use security review for hooks, installers, external calls, file writes, secrets, and auth-like flows.
- Prefer small, cohesive files.
- Prefer explicit manifests over hidden conventions.

## Project layout

```text
agents/      Agent definitions
skills/      Reusable workflows
commands/    Slash commands and command metadata
rules/       Always-on project and harness rules
hooks/       Hook definitions and templates
contexts/    Context templates and memory scopes
config/      Manifests, schemas, defaults
tools/       TypeScript and Python implementation code
scripts/     Validation, packaging, release helpers
```

## Coding rules

- Keep core free and MIT-compatible.
- Do not add telemetry by default.
- Do not add paid-service dependency to required paths.
- Validate external input at boundaries.
- Avoid destructive install behavior; copy or patch only after explicit confirmation.
- Keep generated files reproducible.
- Keep `CLAUDE.md` under 200 lines.

## Architecture rules

- Claude Code adapter owns first implementation.
- Harness-neutral manifests define source of truth.
- Adapters translate manifests into target-specific files.
- Installers must support dry-run.
- Tests must run without external credentials.

## Review checklist

- Required files exist.
- MIT license names Rafi Permana and 2026.
- README explains install, features, comparison, roadmap.
- AGENTS.md explains orchestration and quality gates.
- SOUL.md guarantees free-forever philosophy.
- Package metadata exposes validation commands.
