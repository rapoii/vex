---
name: code-review-flow
description: Review diffs with severity ordering, full-file context, and actionable fixes.
argument-hint: "[branch | file | scope]"
metadata:
  origin: VEX
  category: workflow
  triggers: ["Before merge or PR", "After non-trivial code changes", "When correctness/security confidence matters"]
---

# Code Review Flow

Review code changes systematically. Focus on architecture, correctness, and security.

## When to Activate

- Before creating a pull request.
- Reviewing another developer's pull request.
- After complex, multi-file refactoring.
- Auditing security-sensitive code paths.

## Review Stages

### Stage 1: Context Gathering
1. **Understand Intent**: What problem does this code solve?
2. **Review Diff**: Read the full diff, not just isolated lines.
3. **Read Full Files**: For critical files, read the whole file to understand the context of the change.

### Stage 2: Quality Checklist (The "What to Look For")

#### Architecture & Design
- Does it follow project conventions?
- Is state managed appropriately (e.g., Server vs. Client state)?
- Does it violate DRY, KISS, or YAGNI?
- Are abstractions helpful or premature?

#### Correctness & Logic
- Does it handle edge cases? (Null, undefined, empty collections, large inputs).
- Are async operations handled correctly? (Race conditions, missing awaits).
- Is error handling robust? (No silent swallowing).

#### Security (CRITICAL)
- Are user inputs sanitized/validated?
- Are secrets hardcoded?
- Are there potential injection vulnerabilities (SQL, XSS, Command)?
- Is authorization checked properly?

#### Performance
- Are there N+1 query problems?
- Are large arrays processed inefficiently?
- Is there unnecessary re-rendering (React)?

#### Maintainability
- Is the code readable? Are names descriptive?
- Is complexity manageable? (Avoid deep nesting).
- Are functions focused?
- Is there test coverage for new logic?

### Stage 3: Severity Classification

Categorize findings to guide action:

| Severity | Meaning | Action Required |
|---|---|---|
| **CRITICAL** | Security flaw, data loss risk, hard crash. | **BLOCK**. Must fix immediately. |
| **HIGH** | Major bug, severe performance issue, architectural violation. | **WARN**. Strongly advise fixing before merge. |
| **MEDIUM** | Maintainability issue, minor bug, confusing logic. | **INFO**. Good to fix, but not a blocker. |
| **LOW** | Nitpick, stylistic suggestion, minor optimization. | **NOTE**. Optional. |

## Workflow Execution

1. **Scan Diff**: `git diff main...HEAD` (or relevant branch).
2. **Identify Files**: List files touched.
3. **Deep Dive**: Read specific files using `Read` or `cat`.
4. **Compile Findings**: Group findings by file and severity.
5. **Present Report**: Output structured markdown.

## Example Report Format

```markdown
## Code Review Summary

**Overall Status**: ⚠️ Changes Requested

### 🔴 CRITICAL
- **`src/auth/login.ts` (Line 42)**: SQL Injection vulnerability. User input `req.body.username` is concatenated directly into the query string.
  - **Fix**: Use parameterized queries: `db.query('SELECT * FROM users WHERE username = ?', [username])`.

### 🟠 HIGH
- **`src/components/List.tsx` (Line 15)**: Missing `key` prop in `.map()` loop. Will cause rendering issues.
  - **Fix**: Add a unique key: `<ListItem key={item.id} ... />`.

### 🟡 MEDIUM
- **`src/utils/calc.ts` (Line 80)**: Function `calculateTotal` is 150 lines long. Hard to read.
  - **Suggestion**: Extract discount calculation logic into a separate `calculateDiscount` function.

### 🟢 LOW
- **`src/styles/main.css`**: Inconsistent indentation.
```

## Common Pitfalls

- **Nitpicking**: Focusing on style over substance. Let linters handle formatting.
- **Ignoring Context**: Reviewing a 5-line diff without looking at the surrounding 50 lines.
- **Missing Security Flaws**: Assuming framework magic protects against everything. Always check inputs.
- **Vague Feedback**: Saying "This looks wrong." Instead say: "This causes a memory leak because the event listener is never removed."

## Pipeline

**Previous:** [strict-tdd](../strict-tdd/SKILL.md) — enforce RED/GREEN/REFACTOR before production changes
**Next:** [receiving-code-review](../receiving-code-review/SKILL.md) — process review feedback and resolve comments systematically
