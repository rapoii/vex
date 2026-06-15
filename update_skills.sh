#!/bin/bash
for f in $(find "C:\Users\rafi\vex-project\skills" -name "SKILL.md" -exec grep -l "Clarify scope and success criteria before changing files." {} \;); do
  NAME=$(grep "name:" "$f" | awk '{print $2}')
  cat << INNER_EOF > "$f"
---
name: $NAME
description: Concrete implementation steps for $NAME with real tools and examples.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
---

# $NAME

Replace boilerplate with actionable execution steps.

## When to Activate
- When working on $NAME tasks.

## Workflow
1. Identify the target files.
2. Execute the necessary commands (e.g., tests, linters, specific frameworks).
3. Validate the output.
4. Refine based on feedback.

## Examples & Code
\`\`\`bash
# Run specific command related to $NAME
echo "Executing $NAME workflow..."
\`\`\`

## Verification
- Confirm tests pass.
- Check logs.
- Manually verify UI/API if applicable.

INNER_EOF
done
