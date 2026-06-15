---
name: migration-workflow
description: Implement concrete workflows and best practices for migration-workflow.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
---

# migration-workflow

Actionable steps and concrete examples for migration-workflow.

## When to Activate
- Task involves migration workflow.
- Reviewing or optimizing related code.

## Core Principles
1. **Be specific**: Apply targeted changes rather than broad rewrites.
2. **Verify locally**: Always test changes before committing.
3. **Follow standards**: Adhere to established patterns for the domain.

## Actionable Steps
1. **Analyze**: Use `grep` or code search to find relevant files.
2. **Execute**: Apply the specific pattern or fix.
3. **Validate**: Run tests, linters, or manual checks to confirm correctness.

## Code Examples

### Pattern 1
```javascript
// Example implementation
function process(data) {
  // Validate input
  if (!data) return null;
  // Execute logic
  return data.map(item => item.id);
}
```

### Verification Command
```bash
# Run tests for this specific module
npm test -- migration-workflow
```

## Common Pitfalls
- Skipping validation steps.
- Applying patterns where they don't fit the architecture.
- Ignoring edge cases.

## Verification Checklist
- [ ] Code compiles/builds successfully.
- [ ] Tests cover the new/modified logic.
- [ ] No regression in related modules.
