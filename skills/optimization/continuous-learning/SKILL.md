---
name: continuous-learning
description: Learn reusable VEX instincts from local session history and promote high-confidence rules safely.
---

# Continuous Learning

Use this skill when VEX should learn from repeated local Claude Code sessions.

## Trigger

Run when user asks to learn from sessions, extract patterns, improve future routing, or build instincts.

## Commands

```bash
python tools/vex_instinct.py learn
python tools/vex_instinct.py list
python tools/vex_instinct.py apply
python tools/vex_instinct.py forget <instinct>
```

## Workflow

1. Record sessions first with `python tools/vex_sessions.py record`.
2. Learn instincts with `python tools/vex_instinct.py learn`.
3. Review confidence scores with `python tools/vex_instinct.py list`.
4. Apply only high-confidence instincts with `python tools/vex_instinct.py apply`.
5. Remove stale or noisy instincts with `python tools/vex_instinct.py forget <instinct>`.

## Safety

- Local files only.
- No network calls.
- No automatic promotion without explicit `apply`.
- Generated rules include evidence and confidence.
- Low-confidence patterns stay suggestions.

## Confidence Model

Instinct confidence should consider frequency, success rate, and matching context. Patterns repeated across sessions gain confidence. Failed tool sequences lose confidence. File and hook operations require extra review before promotion.

## Good Instincts

- Repeated Read -> Edit -> test validation flow.
- Repeated hook disable during markdown-only work.
- Repeated token spikes from broad file reads.
- Repeated build failure fixed by same narrow command.

## Bad Instincts

- One-off emergency work.
- Repo-specific file paths.
- Secrets or private transcript text.
- Destructive shortcuts.
- Rules based only on failed sessions.
