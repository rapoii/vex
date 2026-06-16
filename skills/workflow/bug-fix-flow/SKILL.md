---
name: bug-fix-flow
description: Reproduce, isolate, patch, and verify defects without speculative rewrites.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: workflow
  triggers: ["Failing test or user-reported defect", "Production regression", "Unclear runtime error"]
---

# Bug Fix Flow

A systematic approach to debugging and fixing issues without causing regressions.

## When to Activate

- A test is failing.
- A user reported a defect.
- A production error occurred.
- Unexpected runtime behavior is observed.

## The Bug Fix Cycle

### Step 1: Reproduce

Do not touch code until you can reliably reproduce the error.

1. **Gather Information**: What is the expected behavior? What is the actual behavior? What are the steps to reproduce? What environment?
2. **Write a Failing Test (TDD)**: If possible, write an automated test that captures the bug. This proves the bug exists and proves your fix works later.
   - *Example*: If sorting is broken, write `expect(sort([3, 1, 2])).toEqual([1, 2, 3])`. It should fail.

### Step 2: Isolate

Narrow down the location of the bug.

1. **Read the Stack Trace**: Identify the exact file and line number where the error originates.
2. **Trace the Data Flow**: Follow variables backwards from the crash point to see where bad data entered.
3. **Use Binary Search**: If a long block of code is failing, comment out halves to find the culprit.
4. **Inspect State**: Use logging (`console.log`, `print()`) or a debugger to check variable values right before the failure.

### Step 3: Root Cause Analysis

Ask *why* it failed, not just *how* to make the error go away.

- **Bad**: "It crashed because `user` is null. I'll add `if (!user) return;`." (This might mask a deeper issue where `user` *shouldn't* be null).
- **Good**: "It crashed because `user` is null. Why is it null? Because the DB query failed silently. I need to handle the DB error."

### Step 4: Patch

Apply the smallest, safest fix.

- Do not refactor unrelated code while fixing a bug.
- Fix the root cause, not the symptom.
- Ensure the fix doesn't break other features (run existing test suite).

### Step 5: Verify

Prove the fix works.

1. **Run the Reproducer Test**: The failing test from Step 1 should now pass.
2. **Run the Full Test Suite**: Ensure no regressions were introduced.
3. **Manual Check**: If it's a UI bug, run the app and click through the scenario manually.

## Common Pitfalls

- **Shotgun Debugging**: Making random changes hoping it works. This breaks things.
- **Masking Symptoms**: Catching an exception and doing nothing (`try { ... } catch (e) {}`), or adding null checks without understanding why data is null.
- **Feature Creep**: Sneaking in new features or major refactors during a bug fix PR. Keep it focused.
- **Ignoring Edge Cases**: Fixing the bug for the specific reported scenario but ignoring similar scenarios.

## Language/Domain Specific Guidance

### Web/Frontend
- Check browser console for errors.
- Check Network tab for failed API requests or malformed responses.
- Use React/Vue devtools to inspect component state.

### Backend/API
- Check server logs.
- Verify request payload and headers.
- Check database state (did the record actually save?).

### Build/Config
- Clear caches (`rm -rf node_modules/.cache`, etc).
- Check environment variables.
- Verify dependency versions.

## Pipeline

**Previous:** (bug report) — defect report or failing behavior starts fix flow
**Next:** [verification-before-completion](../verification-before-completion/SKILL.md) — prove claimed fixes with real evidence before completion
