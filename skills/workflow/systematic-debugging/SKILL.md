---
name: systematic-debugging
description: Four-phase root-cause debugging workflow from reproduction through guardrails.
---

# Systematic Debugging

Use this skill when a bug is unclear, intermittent, high-impact, or has already resisted quick fixes.

Goal: fix root cause, not symptom.

Core flow:

1. Reproduce
2. Isolate
3. Identify
4. Fix

Each phase has exit criteria. Do not skip ahead unless bug is already fully understood and verified.

## Principles

- Evidence beats guesses.
- One variable changes at time.
- Repro comes before fix.
- Small failing case beats large failing system.
- Root cause beats nearest error message.
- Tests guard behavior; assertions guard invariants; validation guards boundaries.
- Debug notes must distinguish observation from theory.
- If fix is uncertain, do not ship it.
- If bug can recur silently, add guardrail.
- If bug crosses boundary, validate boundary.
- If bug is data-dependent, preserve sample data.
- If bug is time-dependent, capture clocks, ordering, and retries.
- If bug is environment-dependent, record environment.

## Phase 1: Reproduce

Purpose: make failure happen reliably enough to study.

Do not edit production code yet unless edit only adds temporary local instrumentation.

### Gather report facts

Capture:

- What user did.
- What user expected.
- What happened instead.
- Exact error message.
- Exact timestamp if logs exist.
- Affected environment.
- Browser, OS, runtime, package manager, database, service version.
- Account, tenant, feature flags, locale, timezone when relevant.
- Input data and output data.
- Recent deployments or config changes.

Ask for missing facts only if blocked. Otherwise infer from repo, logs, tests, and local reproduction.

### Reproduce manually

Create a repeatable path:

1. Start app or service.
2. Seed or select known data.
3. Execute smallest user action sequence.
4. Record exact result.
5. Repeat once to confirm.

For UI bugs, test golden path and edge cases:

- Fresh load.
- Reload after action.
- Empty state.
- Existing data.
- Slow network if relevant.
- Keyboard-only path if interaction bug.

For API bugs, capture:

- Method.
- Path.
- Headers.
- Auth state.
- Request body.
- Response status.
- Response body.
- Server logs.

For CLI bugs, capture:

- Current working directory.
- Full command.
- Environment variables that affect command.
- Exit code.
- stdout.
- stderr.
- Files changed by command.

### Reproduce with test

Prefer a failing automated test once manual repro exists.

Good repro test traits:

- Fails before fix.
- Fails for same reason as report.
- Minimal setup.
- Deterministic.
- Assert user-visible or boundary behavior.
- Avoid overfitting to current implementation.

Test forms:

- Unit test for pure logic.
- Integration test for API/database behavior.
- E2E test for user flow.
- Regression test for parser, validator, generator, installer, hook, or command.
- Snapshot only when output is intentionally stable and human-reviewable.

### Handle intermittent bugs

If failure is flaky:

- Run loop with fixed seed if available.
- Increase iteration count.
- Capture failure artifacts every run.
- Log scheduling, timing, and ordering.
- Disable unrelated parallelism only for diagnosis.
- Check race conditions, stale cache, retries, timeouts, and shared state.
- Compare pass run and fail run.

Useful artifacts:

- Minimal command to reproduce.
- Seed value.
- Log slice around failure.
- Screenshot or trace.
- Database row sample.
- Network request trace.
- Serialized input fixture.

### Phase 1 exit criteria

Continue only when at least one is true:

- You have reliable manual reproduction.
- You have failing automated test.
- You have captured enough logs/artifacts to study specific failure.

Do not proceed on vague report alone unless environment cannot be run; then state limitation and work from evidence.

## Phase 2: Isolate

Purpose: narrow failure to smallest failing case and smallest responsible area.

Isolation prevents fixing nearby symptom.

### Shrink input

Reduce failing data:

- Remove optional fields.
- Remove unrelated records.
- Shorten strings.
- Reduce list length.
- Use one tenant/account.
- Use one code path.
- Use one command flag.
- Remove timing variation if not relevant.

Keep shrinking until removing anything else makes bug disappear.

### Shrink path

Reduce execution path:

- Bypass UI and call API directly.
- Bypass API and call service function directly.
- Bypass service and call pure helper directly.
- Replace external dependency with local fixture only if dependency behavior is already captured.
- Run one test, then one assertion.

Do not mock unknown behavior. First observe real boundary behavior.

### Split system by boundaries

Find which boundary transforms good state into bad state:

- Browser to server.
- API validator to handler.
- Handler to domain service.
- Domain service to database.
- Database to serializer.
- Generator input to output file.
- Manifest to adapter.
- Installer dry-run to file operation.
- Hook input to hook decision.

At each boundary, capture before and after state.

### Binary search changes

If regression exists:

- Use git log to identify likely window.
- Use tests or repro command across commits when safe.
- Use git bisect only if user state is clean and command is deterministic.
- Compare config, dependencies, lockfiles, generated files, and schema changes.

Do not discard user work to bisect.

### Instrument carefully

Temporary instrumentation should be local, narrow, and removed before final.

Log:

- Values that choose branches.
- Boundary inputs and outputs.
- Error object type and full message.
- Time duration around suspected waits.
- IDs linking logs across layers.

Avoid logging:

- Secrets.
- Tokens.
- Personal data.
- Huge payloads.
- Full environment dumps.

### Compare expected vs actual state

Use tables or bullet lists:

| Point | Expected | Actual | Meaning |
| --- | --- | --- | --- |
| Input validator | field present | field missing | client or schema issue |
| Service call | normalized path | raw path | normalization skipped |
| Output file | stable order | random order | nondeterministic generator |

### Common isolation targets

Check for:

- Off-by-one boundary.
- Null/undefined path.
- Empty collection behavior.
- Locale-sensitive casing.
- Timezone conversion.
- Path separator mismatch.
- Windows vs POSIX shell syntax.
- Case-sensitive filesystem assumption.
- Async function not awaited.
- Promise swallowed.
- Race between cleanup and read.
- Cache invalidation miss.
- Mutable default object.
- Shared singleton state across tests.
- Non-deterministic sort order.
- Regex too broad or too narrow.
- Schema drift.
- Generated file not updated.
- Env var string vs boolean.
- Exit code ignored.

### Phase 2 exit criteria

Continue only when:

- Smallest failing case is known.
- Suspected component or boundary is specific.
- You can explain where good state becomes bad state.

## Phase 3: Identify

Purpose: prove root cause.

Root cause is earliest incorrect decision or missing invariant that explains failure.

### Build causal chain

Write chain internally:

1. Input has property X.
2. Validator accepts X without normalization.
3. Service assumes normalized X.
4. Branch chooses wrong path.
5. Output misses file Y.
6. User sees failure Z.

If chain starts at error message, keep going backward.

### Distinguish symptom from cause

Symptoms:

- Null pointer.
- 500 response.
- Empty output.
- Timeout.
- Flaky test.
- Missing UI element.
- Permission denied.

Possible causes:

- Boundary accepts invalid shape.
- Caller violates invariant.
- Async operation not awaited.
- State mutation shared across requests.
- File path built with wrong separator.
- Retry hides original error.
- Generated manifest omits required file.

Fix cause, not symptom.

### Prove with experiment

Before final fix, prove theory:

- Change one line locally and see repro disappear.
- Add assertion to show invariant violation.
- Add focused test that fails at suspected point.
- Log exact branch decision.
- Replace input with minimal passing variant.
- Compare old and new output.

If experiment disproves theory, return to isolation.

### Check neighboring cases

Once cause found, inspect related cases:

- Same helper used elsewhere.
- Same schema field in other adapters.
- Same generator pattern in other file types.
- Same hook behavior on Windows and POSIX.
- Same command with dry-run and apply mode.
- Same validator in CLI and API.

Do not broaden fix beyond actual repeated pattern.

### Root cause statement format

Use this format:

- Root cause: `<component>` assumes `<invariant>`, but `<boundary>` allows `<violating input/state>`.
- Evidence: `<test/log/manual repro>` shows `<specific transition>`.
- Fix target: enforce or restore invariant at `<location>`.

Examples:

- Root cause: installer assumes target directory exists, but profile validation allows missing install root. Evidence: dry-run passes, apply fails on first copy. Fix target: validate install root before operation plan.
- Root cause: hook parser assumes stdout under 1MB, but command output can exceed threshold. Evidence: failing fixture truncates JSON mid-object. Fix target: size check before parse with clear failure.
- Root cause: generator assumes object key order, but manifest construction merges maps from filesystem traversal. Evidence: repeated runs produce different output. Fix target: stable sort before render.

### Phase 3 exit criteria

Continue only when:

- Root cause statement is precise.
- Evidence proves it.
- Fix target is clear.
- Expected guardrail is known.

## Phase 4: Fix

Purpose: fix root cause and prevent recurrence.

### Choose smallest root-cause fix

Prefer:

- Validate invalid input at boundary.
- Normalize once at boundary.
- Restore invariant near owner.
- Await missing async operation.
- Replace nondeterminism with stable order.
- Preserve original error context.
- Make state local instead of shared.
- Correct schema or manifest source of truth.

Avoid:

- Catch-all fallbacks.
- Swallowing errors.
- Retrying without fixing cause.
- Special-casing one report input when broader invariant exists.
- Changing test expectation to match broken behavior.
- Adding compatibility shim for impossible path.
- Large refactor mixed with bug fix.

### Add guardrails

Defense-in-depth means fix plus prevention.

Guardrail options:

- Regression test for reported behavior.
- Boundary validation for external input.
- Assertion for internal invariant.
- Type narrowing that makes invalid state unrepresentable.
- Schema update.
- Stable sorting for generated output.
- Dry-run check before file write.
- Clear error message with actionable remediation.
- Lint rule or validator when bug is pattern-level.
- Fixture that captures tricky edge case.

Choose guardrail closest to failure mode.

### Verify fix

Run:

- New failing test: fails before, passes after.
- Related existing tests.
- Typecheck or lint if touched typed code.
- Manual repro for user-visible bug.
- UI flow in browser for frontend change.
- Installer or hook dry-run for file-operation change.

If verification cannot run, state exactly why.

### Clean up

Before completion:

- Remove temporary logs.
- Remove diagnostic files unless requested.
- Keep useful regression fixtures.
- Keep code focused.
- Avoid unrelated formatting churn.
- Confirm generated files reproducible if touched.

### Completion report

Report briefly:

- Repro method.
- Root cause.
- Fix location.
- Guardrail added.
- Verification run.

## Debugging checklists

### Runtime crash

- Capture stack trace.
- Identify first app frame.
- Inspect values at crash point.
- Walk backward to invalid value source.
- Add test for invalid value path.
- Fix source or boundary.

### Wrong output

- Capture input and output.
- Define expected output.
- Find transformation step that diverges.
- Add focused assertion around transformation.
- Fix transformation or invariant.
- Add stable fixture.

### Performance regression

- Measure baseline.
- Reproduce under comparable load.
- Profile before optimizing.
- Identify bottleneck.
- Fix bottleneck only.
- Re-measure.
- Add budget or regression test if feasible.

### Flaky test

- Run repeatedly.
- Capture seed/order.
- Check shared state.
- Check timers and async awaits.
- Check filesystem cleanup.
- Check network assumptions.
- Fix nondeterminism.
- Keep regression proving stable behavior.

### Hook or installer bug

- Use dry-run first.
- Capture planned operations.
- Verify no destructive behavior.
- Test missing files, existing files, permission denied, Windows paths, POSIX paths.
- Validate external input before writes.
- Preserve user files unless explicit confirmation exists.

### Generator bug

- Compare manifest input to generated output.
- Check stable ordering.
- Check missing required files.
- Check schema validation.
- Check path normalization.
- Add golden fixture if output intentionally stable.

## Anti-patterns

Do not:

- Patch first, investigate later.
- Add broad try/catch to hide failure.
- Add sleep to fix race without causal proof.
- Delete failing test.
- Over-mock boundary before observing it.
- Use production data without minimizing or sanitizing.
- Mix cleanup refactor with bug fix.
- Claim fixed without running repro.
- Stop at first symptom.
- Ignore guardrails.

## Quick template

```text
Repro:
- Command/steps:
- Expected:
- Actual:

Isolation:
- Smallest failing case:
- Boundary where state changes:

Root cause:
- Component:
- Broken invariant:
- Evidence:

Fix:
- Code change:
- Guardrail:
- Verification:
```
