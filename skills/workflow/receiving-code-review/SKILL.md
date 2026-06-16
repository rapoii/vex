---
name: receiving-code-review
description: How to process, address, and respond to code review feedback efficiently.
category: workflow
whenToUse: When receiving feedback on a PR, processing review comments, deciding when to push back, or resolving conflicting suggestions.
---

# Receiving Code Review

Processing code review feedback systematically prevents endless review cycles, builds trust, and ensures code quality.

## Triggers

Activate this workflow when:
- Reviewer leaves comments on a PR
- Review is marked "Changes requested"
- Multiple reviewers provide conflicting feedback
- You need to evaluate whether to accept a suggestion or push back

## Workflow: Systematic Review Processing

### 1. Categorize Feedback

Read through all comments before starting any work. Group them into:
- **Blockers / Bugs:** Must fix (logic errors, security risks, test failures).
- **Architecture / Design:** Structural changes that require discussion.
- **Style / Conventions:** Aligning with project standards.
- **Nitpicks:** Minor preference changes, typos, naming tweaks.

### 2. Evaluate and Decide

For each comment, decide:
- **Accept:** The feedback is valid and improves the code. Implement it.
- **Discuss/Push Back:** The feedback contradicts requirements, breaks edge cases, or introduces risk. Respond with reasoning.
- **Acknowledge:** Non-actionable feedback or praise.

### 3. Implement Changes Systematically

- Fix bugs and structural issues first.
- Address style and nitpicks last.
- Do NOT rewrite unrelated code while fixing review comments. Scope creep causes new bugs.
- If a suggested change touches many files, pause and confirm the scope with the reviewer.

### 4. Respond and Request Re-review

- Reply to every comment.
- "Done" is sufficient for simple fixes.
- Explain *how* you fixed complex issues.
- Push changes as a new commit (do not amend yet if reviewers need to see the delta).
- Re-request review.

## Pushing Back vs Accepting

Do not blindly accept all feedback. You own the code.

**When to Accept:**
- It catches a genuine bug or edge case.
- It aligns with the project's established style guide or architecture (even if you prefer a different style).
- The suggested change is small, low-risk, and makes the code cleaner.
- The reviewer has more context on the specific domain.

**When to Push Back:**

| Situation | Example Good Response | Example Bad Response |
|-----------|----------------------|----------------------|
| Breaches requirements | "If we make this sync, the UI will freeze during large uploads per requirement doc X. Should we revisit the requirement?" | "No, I want it async." |
| Introduces a bug | "Good catch on the simplicity, but using `map` here breaks when the array contains nulls (see line 42). I'll add a comment clarifying why." | "That doesn't work." |
| Out of scope | "Refactoring the entire auth module is a great idea, but outside the scope of this bug fix. I've created ticket PROJ-123 to track it." | "I don't have time for that." |
| Performance risk | "This abstraction looks cleaner, but moving this inside the loop changes the complexity from O(n) to O(n²). I've run benchmarks showing a 4x slowdown." | "Too slow." |

## Handling Conflicting Feedback

When Reviewer A says X, and Reviewer B says Y:
1. Do not silently pick one.
2. Tag both reviewers in a single comment summarizing the conflict.
3. Propose a path forward based on project principles.
4. If unresolved asynchronously, schedule a quick synchronous sync.

*Example:* "@ReviewerA @ReviewerB, A suggests extracting this to a service, while B suggests keeping it inline for locality. Given our principle of 'KISS for single-use logic', I lean toward B, but let me know what you think."

## Handling Nitpicks Gracefully

Nitpicks (nits) are minor preference suggestions.
- **If it takes < 2 minutes:** Just do it. It builds goodwill.
- **If there are dozens of nits:** Fix them, but open a follow-up task to update the linter/formatter to catch them automatically. Never argue about style manually; automate it.
- **If the nit delays a critical hotfix:** Acknowledge it, merge the fix, and address the nit in a follow-up PR.

## Code Examples: Implementing Feedback

### Example 1: Suggestion to extract logic
*Comment:* "This regex parsing is getting complex. Extract to a helper?"

*Implementation:*
```javascript
// BEFORE
function processUser(input) {
  const email = input.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)?.[0];
  // ...
}

// AFTER
function extractEmail(input) {
  return input.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)?.[0];
}

function processUser(input) {
  const email = extractEmail(input);
  // ...
}
```

### Example 2: Handling a misunderstood requirement
*Comment:* "Why aren't we validating the user ID here?"

*Response:* "The user ID is guaranteed to be valid at this layer because `authMiddleware` validates it upstream. Adding validation here would be redundant. Should I add an assertion or comment to make this clearer to future readers?"

## Verification Steps

Before re-requesting review:
1. Run `git diff` against your previous commit to ensure you only changed what was requested.
2. Run tests to ensure your fixes didn't break existing behavior.
3. Verify all comments are marked as resolved or have a reply.

## Related Skills
- `pr-workflow`
- `code-review-flow`

## Pipeline

**Previous:** [code-review-flow](../code-review-flow/SKILL.md) — review diffs with severity ordering and actionable fixes
**Next:** [verification-before-completion](../verification-before-completion/SKILL.md) — prove claimed fixes with real evidence before completion
