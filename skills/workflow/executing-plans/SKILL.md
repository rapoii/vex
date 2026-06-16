---
name: executing-plans
description: How to systematically execute an approved implementation plan in batches with human checkpoints.
category: workflow
whenToUse: When an approved plan exists and execution begins. Useful for large refactors, complex feature additions, or multi-step migrations.
---

# Executing Plans

Complex tasks fail when executed chaotically. This workflow ensures systematic execution of an approved plan, minimizing risk through batching, validation, and human checkpoints.

## Triggers

Activate this workflow when:
- An approved `plan.md` or task list exists.
- The user instructs you to "start", "execute", or "begin the plan".
- A multi-step migration or large refactor is ready for implementation.

## Pre-Execution Checklist

Before writing code:
1. **Understand State:** Verify the current branch is correct and clean.
2. **Review Plan:** Read the approved plan entirely to refresh context.
3. **Verify Prerequisites:** Ensure necessary tools, dependencies, or environment variables exist.
4. **Identify Batches:** Group plan steps into independent, testable batches.

## Workflow: Batch Execution

Execute the plan in discrete batches. A batch is a logical unit of work that leaves the codebase in a functional state.

### 1. Decompose into Batches
Group tasks logically. Example:
- **Batch 1: Scaffolding.** Create files, define interfaces, add skeleton tests.
- **Batch 2: Core Logic.** Implement pure functions, data models, or core algorithms.
- **Batch 3: Integration.** Connect core logic to API/DB/UI.
- **Batch 4: Polish.** Error handling, logging, final tests.

### 2. Execute Batch
For each batch:
- Execute the specific steps using TDD (if applicable).
- Keep changes scoped *strictly* to the current batch. Do not fix unrelated issues.
- If a step requires significant architectural changes not in the plan, STOP and re-evaluate.

### 3. Verify Batch
Before moving to the next batch:
- Run relevant tests.
- Run linter/type-checker.
- Ensure the app builds.
- The codebase MUST be in a working state.

### 4. Human Checkpoints
Stop and ask for user review between batches, especially when:
- Completing a destructive operation (e.g., dropping a table).
- Implementing security-sensitive logic (auth, permissions).
- Making architectural choices with long-term impact.
- The batch took significantly longer or required more complexity than anticipated.

*Example Checkpoint Message:*
"Batch 1 (Scaffolding and Interfaces) is complete. Tests pass. Please review the new `AuthService` interface before I proceed to implementation in Batch 2."

## Progress Tracking

Maintain visibility into execution state.

1. **Update Tracking Documents:** If using `plan.md` or a task tracker, mark items as complete explicitly.
2. **Use TodoWrite:** If hooks are configured, use `TodoWrite` to update task status in the UI.
3. **Status Reports:** Start each response with a brief status update:
   - What was just done.
   - Current blockers (if any).
   - What is next.

*Example Status Update:*
> **Status:** 2/4 batches complete.
> **Just finished:** Implemented API routing and middleware.
> **Next:** Writing integration tests for the routes.

## Handling Failures Mid-Batch

If execution fails (tests break, unexpected complexity arises):

1. **Diagnose First:** Don't thrash. Understand why the failure occurred.
2. **Isolate:** Can the failure be fixed within the current batch scope?
3. **Rollback if Necessary:** If the approach is fundamentally flawed, reset the working tree (`git restore .`) to the last known good state (start of the batch).
4. **Re-plan:** Document the failure, adjust the plan, and present the new approach to the user for approval.

## Handling Scope Changes

If the user changes requirements during execution:
1. **Pause Execution:** Stop current work.
2. **Assess Impact:** Evaluate how the change affects completed and future batches.
3. **Update Plan:** Modify the plan document to reflect the new scope.
4. **Confirm:** Explicitly confirm the scope change and its implications (e.g., "This new requirement invalidates Batch 1. I will need to rewrite the interface. Proceed?")

## Post-Execution

When all batches are complete:
1. Run the full test suite.
2. Perform a final code review (using the `code-reviewer` agent).
3. Update documentation to reflect the new reality.
4. Provide a final summary to the user detailing what was changed and any manual verification steps they should take.

## Communication and Transparency

When executing a plan, constant communication builds trust. 
- **Pre-batch:** Briefly state what you are about to do.
- **In-progress:** If a task takes multiple turns or requires investigation, output a short update before continuing.
- **Post-batch:** Summarize what was completed and ask for permission to proceed.

### Example Interaction

**Assistant:**
"Starting Batch 2: Core Logic. I will implement the user parsing function and add unit tests."
*[Assistant writes code]*
**Assistant:**
"Batch 2 complete. `parseUser` function added and 5 tests pass. Ready for Batch 3: Integration. Shall I proceed?"
**User:**
"Yes, go ahead."

## Tools to Avoid During Execution

Do not use high-level planning tools or agents during execution unless replanning is explicitly required. Stick to execution tools (`Bash`, `Write`, `Edit`, `Read`). Spawning architectural agents during a batch execution breaks focus and risks introducing scope creep.

## Related Skills
- `better-plan`
- `tdd-workflow`
- `refactor-flow`

## Pipeline

**Previous:** [worktree-isolation](../worktree-isolation/SKILL.md) — isolate implementation work on safe branch or worktree
**Next:** [strict-tdd](../strict-tdd/SKILL.md) — enforce RED/GREEN/REFACTOR before production changes
