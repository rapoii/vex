---
description: Review local diff or PR and return severity-ordered findings.
argument-hint: "[scope | issue | blank for current diff]"
---

# Code Review

**Input**: $ARGUMENTS

## Workflow

1. Determine scope from arguments, current diff, or project context.
2. Read relevant files and existing project guidance.
3. Use matching VEX/ECC skill or agent when task complexity warrants it.
4. Execute smallest safe action set.
5. Validate with targeted commands or manual verification.
6. Report changed paths, evidence, and unresolved risks.

## Output

- Scope reviewed or changed.
- Validation performed.
- Findings or next steps with `file:line` when applicable.
