---
name: verification-before-completion
description: Verify claimed fixes with real evidence before declaring work complete.
argument-hint: "[bug | fix | branch | pr]"
metadata:
  origin: VEX
  category: workflow
  inspiration: Superpowers
  triggers: ["User says done", "User says fixed", "Before final status", "After code changes"]
---

# Verification Before Completion

Use this workflow when work appears finished but has not been proven.

This adapts Superpowers verification discipline for VEX: never accept "done" or "fixed" as truth until the actual behavior, tests, and edge cases have been checked.

## When to Activate

- User says a bug is "done" or "fixed".
- You are about to claim success.
- A subagent reports completion.
- Tests were changed and may no longer prove the intended behavior.
- A UI, CLI, hook, installer, generator, or validator changed.
- A regression was possible in nearby behavior.
- The fix depends on environment state, filesystem paths, subprocesses, or external tools.
- A previous attempt failed or was only partially verified.
- The task touched security-sensitive boundaries.
- The user asks whether a change works.

## When Not to Activate

- No code, docs, config, generated file, or runtime behavior changed.
- User asked only for static explanation.
- Verification requires credentials or shared systems the user has not authorized.
- The requested action is destructive and needs confirmation first.

## Core Rule

Do not declare completion from intent.

Completion requires evidence:

- Expected command passed.
- Specific bug no longer reproduces.
- Important edge cases are checked.
- No obvious regression appears.
- Evidence is reported precisely.

## Workflow

### Step 1: Restate Claim

Write the exact claim being verified.

Good claim:

```text
The install dry-run no longer writes files and exits 0.
```

Bad claim:

```text
Install fixed.
```

Make claim observable.

If claim cannot be observed, ask for success criteria.

### Step 2: Identify Verification Surface

List changed behavior surfaces:

- Unit tests
- Integration tests
- Build
- Lint
- Type check
- CLI command
- Browser interaction
- Installer dry-run
- Generated output
- Hook behavior
- Database migration
- API response
- Security boundary

Pick checks that prove behavior, not merely syntax.

### Step 3: Run Baseline-Relevant Tests

Run tests closest to the change first.

Examples:

```bash
npm test -- tests/install.test.js
pytest tests/test_installer.py
node tests/test-workflow-pack.js
```

Then run broader validation when cheap:

```bash
npm test
npm run build
npm run lint
```

Do not hide failing tests.

If unrelated tests fail, identify why and report separately.

### Step 4: Reproduce Original Bug Path

Verify the bug path itself.

For bug fixes:

1. Recreate failing input or flow.
2. Confirm old failure condition is absent.
3. Confirm expected output is present.
4. Confirm exit code or status is correct.
5. Confirm logs do not show hidden exceptions.

A unit test alone is not enough when original bug was found through runtime behavior.

### Step 5: Check Edge Cases

Select edge cases based on risk.

Common edge cases:

- Empty input
- Missing file
- Existing file
- Invalid config
- Windows path
- POSIX path
- Spaces in path
- Permission denied
- Network unavailable
- Duplicate names
- Large input
- Partial failure
- Concurrent invocation

Do not invent huge edge matrices.

Pick the cases most likely to break the changed code.

### Step 6: Inspect Output Artifacts

When code generates files, inspect output.

Check:

- File paths are correct.
- Content is deterministic.
- No secrets are included.
- Metadata matches schema.
- Line endings are acceptable.
- Re-running does not create drift.

For VEX packs, verify manifests and generated docs when touched.

### Step 7: Verify No Regression In Neighbor Behavior

Run a nearby unchanged path.

Examples:

- If adding a skill, list skills or run pack validator.
- If changing installer, test dry-run and no-op path.
- If changing hook, test normal allowed event and ignored event.
- If changing CLI flag, test default behavior too.

Regression check should be small and targeted.

### Step 8: Record Evidence

Report evidence in final response.

Use this shape:

```text
Verified:
- Command: <command>
- Result: <pass/fail>
- Specific behavior: <observed fact>
- Edge case: <observed fact>
```

Do not say "should work" after verification.

Say "verified by ..." or "not verified because ...".

### Step 9: Handle Failed Verification

If verification fails:

1. Stop claiming success.
2. Capture exact failure.
3. Decide whether failure is caused by your change, baseline, or environment.
4. Fix if in scope.
5. Re-run failed verification.
6. Only proceed after passing evidence.

Do not mark task complete while critical verification fails.

### Step 10: Human Checkpoint

Ask user before expanding scope when:

- Fix requires unrelated refactor.
- Required credentials are missing.
- Verification would touch production or shared services.
- Destructive cleanup is needed.
- Expected behavior is ambiguous.

## Verification Checklist

- [ ] Claim is specific and observable.
- [ ] Targeted tests ran.
- [ ] Build or type check ran when applicable.
- [ ] Lint ran when applicable.
- [ ] Original bug path was exercised.
- [ ] Important edge cases were checked.
- [ ] Generated files or artifacts were inspected.
- [ ] Nearby regression path was checked.
- [ ] Failures were not hidden.
- [ ] Final response includes commands and results.
- [ ] Success is only declared after evidence passes.

## Superpowers Discipline

Superpowers methodology treats "done" as untrusted until verified.

The useful habit is skepticism:

- A green test can test wrong behavior.
- A passing build can hide broken runtime flow.
- A subagent can report success without checking the actual diff.
- A UI can compile but fail in browser.
- A CLI can pass on POSIX and fail on Windows paths.

Use verification to close the loop between intended fix and real behavior.

## Evidence Quality

Strong evidence:

- Reproduces exact previous failure path.
- Uses real command or UI flow.
- Checks observable output.
- Includes exit code or test result.
- Covers at least one risky edge case.

Weak evidence:

- "Code looks right."
- "Tests should pass."
- "Subagent said fixed."
- "No syntax errors visible."
- "I changed the condition."

Prefer one strong check over many weak statements.

## Output Format

Return:

```text
Claim verified:
Commands run:
Behavior checked:
Edge cases checked:
Regression check:
Result:
Remaining risk:
```

If not verified, return:

```text
Not verified:
Blocker:
What was checked:
Next required step:
Decision needed:
```

## Anti-Patterns

- Declaring success immediately after editing.
- Trusting subagent completion without evidence.
- Running only broad tests and skipping bug reproduction.
- Ignoring failing tests as "probably unrelated" without explanation.
- Skipping UI verification for frontend changes.
- Skipping dry-run for installers.
- Skipping security review for hooks or file writes.
- Changing tests to fit broken code.
- Reporting "all good" without command names.

## VEX-Specific Notes

For skills and agents:

- Run pack tests that validate frontmatter and required sections.
- Check line-count contracts when required.
- Verify skill names match directory names.
- Verify agent names match file names.
- Update orchestration docs if counts or routes changed.

For installers and hooks:

- Prefer dry-run first.
- Verify no unintended writes.
- Verify Windows and POSIX path handling when practical.
- Use security review before final success.
