---
name: requesting-code-review
description: Structure code review requests with context, risk, and actionable reviewer focus.
argument-hint: "[diff | branch | pr | files]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["Before asking for review", "Before PR", "After implementation", "When review focus matters"]
---

# Requesting Code Review

Use this workflow before asking a human or agent to review code.

This adapts Superpowers review-request discipline for VEX: reviewers find better issues when they know what changed, why it changed, where risk lives, and what must block progress.

## When to Activate

- You finished a feature, fix, refactor, migration, or docs pack change.
- You are about to request code-reviewer or human review.
- Review scope spans multiple files.
- Change has risky areas that need attention.
- You need a PR description that guides reviewers.
- A previous review missed context.
- You need to distinguish blockers from deferrable feedback.
- You are coordinating multiple specialist reviewers.

## When Not to Activate

- Change is a one-line typo with no behavior impact.
- User asked for direct review without extra packaging.
- You do not yet understand what changed.
- Tests have not been run and failures are unknown.
- Review would expose secrets or private unrelated context.

## Core Rule

A good review request reduces reviewer guesswork.

It answers:

- What changed?
- Why changed?
- What should reviewer focus on?
- What is risky?
- What was verified?
- What is out of scope?
- Which findings block progress?

## Workflow

### Step 1: Summarize Intent

Write one or two sentences explaining goal.

Good:

```text
Adds workflow skills from Superpowers so VEX exposes missing branch-finishing and verification guidance.
```

Bad:

```text
Updated files.
```

Intent should explain why change exists, not list every file.

### Step 2: Summarize What Changed

Group changes by purpose.

Example:

```text
- Added four workflow skill docs with frontmatter, activation guidance, workflows, and verification checklists.
- Added four agent definitions with prompt defense baseline, role, workflow, and output format.
- Updated validation test enumerations and AGENTS.md count.
```

Do not paste full diff.

Do not hide generated files.

### Step 3: Highlight Risky Areas

Name areas where bugs are most likely.

Risk examples:

- Installer writes or deletes files.
- Hook executes shell commands.
- Agent prompt can leak secrets or follow injected instructions.
- Skill frontmatter may break parser.
- Validation test may enforce wrong path.
- Generated docs may drift from manifest.
- Migration may lock table.
- UI flow may regress existing interaction.

Reviewer time should go where impact is high.

### Step 4: Point To Specific Files Or Functions

Give exact paths and symbols.

Use:

```text
Please review:
- skills/workflow/verification-before-completion/SKILL.md — activation and anti-patterns
- agents/core/docs-lookup.md — external docs safety constraints
- tests/test-workflow-pack.js — contract additions
```

For code, include functions when known:

```text
- tools/install.ts:applyPatch
- hooks/scripts/session-start.py:main
```

Specific targets beat broad requests.

### Step 5: State Verification Performed

List commands and results.

Example:

```text
Verification:
- node tests/test-workflow-pack.js — pass
- npm test — pass
```

If not run, say why.

Do not claim tests passed without running them.

### Step 6: State Review Rules

Tell reviewer how to classify findings.

Critical issues block progress.

Critical examples:

- Data loss
- Security vulnerability
- Broken required behavior
- Failing tests caused by change
- Installer destructive behavior
- Secret exposure
- Incorrect external call behavior

Non-critical issues can be deferred.

Non-critical examples:

- Naming preference
- Optional refactor
- Formatting lint already handles
- Minor docs wording
- Follow-up feature suggestion

Make priority explicit.

### Step 7: Mention Out Of Scope

Declare scope boundaries.

Example:

```text
Out of scope:
- Rewriting existing workflow skills.
- Changing harness adapter schema.
- Adding generated registry output.
```

This prevents review from becoming redesign.

### Step 8: Choose Reviewers

Match reviewer to risk.

- code-reviewer: correctness, maintainability, scope control.
- security-reviewer: hooks, installers, external calls, secrets, auth-like flows.
- database-reviewer: migrations, queries, indexes, constraints.
- mle-reviewer: training, evaluation, leakage, reproducibility.
- e2e-runner: browser or end-to-end user flow validation.
- docs-lookup: current external API docs and examples.

Use multiple reviewers when risks differ.

### Step 9: Ask Direct Questions

End with focused asks.

Examples:

```text
Please check whether test contracts cover all new files and whether any new agent prompt lacks prompt-injection defense.
```

```text
Please verify migration order avoids table locks on large installs.
```

Avoid vague asks like "thoughts?" when blocking review is needed.

### Step 10: Collect And Act

When review returns:

- Fix critical issues before progress.
- Fix high-confidence correctness bugs.
- Defer non-critical issues only with explicit note.
- Push back on suggestions that break requirements.
- Ask clarifying questions for ambiguous blockers.

## Verification Checklist

- [ ] Intent summary explains why.
- [ ] Change summary groups work by purpose.
- [ ] Risky areas are highlighted.
- [ ] Specific files/functions needing review are named.
- [ ] Tests and validation commands are listed.
- [ ] Missing verification is disclosed.
- [ ] Critical findings are defined as blockers.
- [ ] Non-critical findings are defined as deferrable.
- [ ] Out-of-scope topics are stated.
- [ ] Reviewer type matches risk area.
- [ ] Review ask includes direct questions.

## Superpowers Discipline

Superpowers code review requests are context packets.

The requester does preparation so reviewer can spend energy on judgment.

Useful habits:

- Summarize why, not just what.
- Point at danger zones.
- Give reproducible verification.
- Separate blockers from suggestions.
- Prevent scope drift.
- Route to specialist reviewers.

A review request that says "please review" wastes reviewer attention.

A review request that says "please inspect installer write safety and frontmatter parser compatibility" gets better defects.

## Request Template

```markdown
## Context
<why this change exists>

## Changes
- <grouped change>
- <grouped change>

## Please focus on
- <file or function>: <risk/question>
- <file or function>: <risk/question>

## Risk areas
- <risk>
- <risk>

## Verification
- `<command>` — <result>
- `<command>` — <result>

## Blocking criteria
Critical issues block progress: security flaw, data loss, broken required behavior, failing validation, or irreversible unsafe action.
Non-critical issues may be deferred: naming, optional cleanup, wording, small style suggestions.

## Out of scope
- <thing not being reviewed>
```

## Anti-Patterns

- Asking for review with no context.
- Dumping full diff instead of summary.
- Hiding failing tests.
- Asking reviewer to infer intended behavior.
- Treating all feedback as equally blocking.
- Letting optional refactors block urgent fixes.
- Ignoring critical findings because they are inconvenient.
- Requesting security review without authorization context.
- Sending broad review to wrong specialist.
- Forgetting to mention generated files.

## VEX-Specific Notes

For VEX changes, include:

- Whether core free/MIT constraints changed.
- Whether any telemetry, paid dependency, or external service was added.
- Whether hooks, installers, generated files, or file writes changed.
- Whether skills or agents include required frontmatter.
- Whether tests run without external credentials.
- Whether CLAUDE.md remains under 200 lines if touched.

Use requesting-code-review before code-review-flow when review quality depends on scope context.
