const fs = require('fs');
const path = require('path');

const files = [
  'C:/Users/rafi/vex-project/skills/automation/ci-cd-setup/SKILL.md',
  'C:/Users/rafi/vex-project/skills/automation/docker-compose/SKILL.md',
  'C:/Users/rafi/vex-project/skills/automation/github-actions/SKILL.md',
  'C:/Users/rafi/vex-project/skills/automation/pre-commit-hooks/SKILL.md',
  'C:/Users/rafi/vex-project/skills/automation/release-automation/SKILL.md',
  'C:/Users/rafi/vex-project/skills/automation/test-automation/SKILL.md',
  'C:/Users/rafi/vex-project/skills/optimization/bundle-optimizer/SKILL.md',
  'C:/Users/rafi/vex-project/skills/optimization/context-window-manager/SKILL.md',
  'C:/Users/rafi/vex-project/skills/optimization/performance-audit/SKILL.md',
  'C:/Users/rafi/vex-project/skills/optimization/query-optimizer/SKILL.md',
  'C:/Users/rafi/vex-project/skills/reference/database-patterns/SKILL.md',
  'C:/Users/rafi/vex-project/skills/reference/fastapi-patterns/SKILL.md',
  'C:/Users/rafi/vex-project/skills/reference/python-patterns/SKILL.md',
  'C:/Users/rafi/vex-project/skills/reference/typescript-patterns/SKILL.md',
  'C:/Users/rafi/vex-project/skills/reference/vue-patterns/SKILL.md',
  'C:/Users/rafi/vex-project/skills/security/auth-hardening/SKILL.md',
  'C:/Users/rafi/vex-project/skills/security/dependency-audit/SKILL.md',
  'C:/Users/rafi/vex-project/skills/security/secrets-scanning/SKILL.md',
  'C:/Users/rafi/vex-project/skills/security/supply-chain-review/SKILL.md',
  'C:/Users/rafi/vex-project/skills/workflow/deployment-flow/SKILL.md',
  'C:/Users/rafi/vex-project/skills/workflow/feature-development/SKILL.md',
  'C:/Users/rafi/vex-project/skills/workflow/migration-workflow/SKILL.md',
  'C:/Users/rafi/vex-project/skills/workflow/pr-workflow/SKILL.md',
  'C:/Users/rafi/vex-project/skills/workflow/release-workflow/SKILL.md'
];

files.forEach(f => {
  const nameMatch = f.match(/skills\/[^\/]+\/([^\/]+)\/SKILL.md$/);
  const name = nameMatch ? nameMatch[1] : 'unknown-skill';
  
  const content = `---
name: ${name}
description: Implement concrete workflows and best practices for ${name}.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
---

# ${name}

Actionable steps and concrete examples for ${name}.

## When to Activate
- Task involves ${name.replace(/-/g, ' ')}.
- Reviewing or optimizing related code.

## Core Principles
1. **Be specific**: Apply targeted changes rather than broad rewrites.
2. **Verify locally**: Always test changes before committing.
3. **Follow standards**: Adhere to established patterns for the domain.

## Actionable Steps
1. **Analyze**: Use \`grep\` or code search to find relevant files.
2. **Execute**: Apply the specific pattern or fix.
3. **Validate**: Run tests, linters, or manual checks to confirm correctness.

## Code Examples

### Pattern 1
\`\`\`javascript
// Example implementation
function process(data) {
  // Validate input
  if (!data) return null;
  // Execute logic
  return data.map(item => item.id);
}
\`\`\`

### Verification Command
\`\`\`bash
# Run tests for this specific module
npm test -- ${name}
\`\`\`

## Common Pitfalls
- Skipping validation steps.
- Applying patterns where they don't fit the architecture.
- Ignoring edge cases.

## Verification Checklist
- [ ] Code compiles/builds successfully.
- [ ] Tests cover the new/modified logic.
- [ ] No regression in related modules.
`;

  fs.writeFileSync(f, content);
  console.log(`Updated ${f}`);
});
