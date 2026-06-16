---
name: multi-backend
description: Backend-focused multi-model workflow for APIs, data, jobs, and security.
argument-hint: "[endpoint | service | migration | blank for current diff]"
---

# Multi Backend

**Input**: $ARGUMENTS

## Purpose

Coordinate backend work across API design, data integrity, security, and tests.
Use this for server code, migrations, queues, auth-like flows, and integrations.
Favor explicit boundaries and deterministic validation.

## Workflow

1. Use Sonnet to map routes, services, schemas, and call graph.
2. Use database agent or Opus for schema and migration risk.
3. Use security reviewer for input, auth, secrets, and file writes.
4. Use Sonnet to implement endpoint, service, and tests.
5. Use Opus when API contract or persistence model is unclear.
6. Run unit tests, integration tests, and relevant validators.
7. Review error handling only at external boundaries.
8. Summarize behavior, compatibility changes, and rollout concerns.

## Model Selection

- Sonnet: implementation, API wiring, test updates, build repair.
- Opus: data model, transaction boundaries, concurrency, hard tradeoffs.
- Haiku: route inventory, config lists, generated manifests.

## Rationale

Backend failures often affect data and shared contracts.
Use deeper reasoning for persistence and contract decisions.
Use faster models for codebase mapping and routine changes.

## Guardrails

- Validate external input at boundaries.
- Do not add telemetry or paid services by default.
- Keep migrations reversible where possible.
- Avoid hidden conventions; update manifests explicitly.

## Output

- API or job behavior changed.
- Data and security risks checked.
- Commands run with pass/fail status.
