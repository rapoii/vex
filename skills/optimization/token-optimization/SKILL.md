---
name: token-optimization
description: Advanced token management for VEX prompts, context windows, model routing, and cost-aware execution.
---

# Token Optimization

Use this skill when work needs lower token cost, faster runs, cleaner context, or model routing discipline.

## Trigger

Use when user asks to optimize prompts, reduce context, manage cost, choose models, compress history, or analyze token waste.

## Commands

```bash
python tools/vex_optimize.py analyze
python tools/vex_optimize.py suggest --task "describe task"
python tools/vex_optimize.py slim "prompt text"
```

## Goals

- Preserve correctness.
- Drop irrelevant context.
- Keep evidence exact.
- Route tasks to right model.
- Avoid repeating large outputs.
- Avoid over-reading files.
- Avoid broad searches when narrow search works.
- Keep session history useful but compact.

## Prompt slimming

1. Remove pleasantries.
2. Remove duplicated asks.
3. Remove vague urgency words.
4. Keep exact paths.
5. Keep exact error text.
6. Keep required output format.
7. Keep constraints that affect safety.
8. Remove background not used by decision.
9. Replace paragraphs with bullets.
10. Replace examples with one canonical example.
11. Replace repeated file lists with globs only when exact enough.
12. Replace generic goals with measurable success criteria.
13. Remove “be comprehensive” unless coverage needs depth.
14. Remove “best practices” when repo conventions decide.
15. Remove “modern” unless version matters.
16. Remove “clean” unless design quality is being judged.
17. Remove old failed attempts unless they change next step.
18. Collapse stack traces to first failing frame plus root cause line.
19. Collapse logs to first error, last error, and command exit code.
20. Keep commands exactly as run.

## Prompt structure

1. Task: one sentence.
2. Scope: files, folders, or subsystem.
3. Constraints: dependency, security, compatibility, style.
4. Evidence: error, diff, or observed behavior.
5. Output: patch, plan, review, or command.
6. Validation: tests or manual checks expected.

## Bad prompt shape

Long narrative with repeated context, unclear target, many optional asks, and no success criteria.

## Good prompt shape

“Fix `tools/vex_sessions.py` export. `python -m unittest tests/test_vex_sessions.py -v` fails because CSV header missing `tokens_out`. Keep stdlib only. Return patch and validation result.”

## Context priority ranking

1. Current user request.
2. Safety constraints.
3. Current failing command output.
4. Relevant changed files.
5. Public API contracts.
6. Tests that define behavior.
7. Existing project instructions.
8. Similar code patterns.
9. Historical notes.
10. Nice-to-have background.

## Context removal rules

1. Drop content not referenced by task.
2. Drop duplicate command output after first occurrence.
3. Drop generated files unless reviewing generated output.
4. Drop old plan steps already completed.
5. Drop stale recommendations contradicted by current code.
6. Drop full file contents after extracting exact line ranges.
7. Drop dependency docs after extracting used API facts.
8. Drop raw JSON when summary fields are enough.
9. Drop broad directory listings after target files found.
10. Drop agent reports after confirmed findings are copied into short list.

## File reading strategy

1. Read known target file directly.
2. Use Grep for exact symbol or error.
3. Use Glob for known file patterns.
4. Use Explore agent only for broad searches beyond three queries.
5. Read line ranges, not whole huge files.
6. Avoid rereading files immediately after Edit.
7. Prefer tests over implementation when learning expected behavior.
8. Prefer manifests over inferred conventions.
9. Prefer current files over memory.
10. Prefer narrow diffs over entire repo scans.

## Search strategy

1. Search exact error string first.
2. Search command name second.
3. Search function/class symbol third.
4. Search config keys fourth.
5. Search broad concepts last.
6. Stop searching when enough evidence exists.
7. Do not fan out redundant searches.
8. Share one search result among follow-up steps.
9. Ask Explore agent for open-ended search only once.
10. Use results to pick files, then read those files.

## Model selection

### Opus

Use Opus for:

- Architecture decisions.
- Security-sensitive design.
- Ambiguous bug root cause.
- Multi-system migrations.
- Adversarial review synthesis.
- High-stakes release decisions.
- Complex tradeoff analysis.

### Sonnet

Use Sonnet for:

- Normal coding.
- Test implementation.
- Refactors with clear scope.
- Build fixes.
- API wiring.
- Documentation updates with code awareness.
- Most reviewer agents.

### Haiku

Use Haiku for:

- Simple classification.
- First-pass search summaries.
- Repetitive extraction.
- Log bucketing.
- Lightweight generated text.
- Low-risk formatting suggestions.
- Quick sanity checks.

## Routing rules

1. If task asks “design”, “architecture”, “tradeoff”, route Opus.
2. If task asks “implement”, “fix”, “test”, route Sonnet.
3. If task asks “classify”, “summarize”, “search”, route Haiku.
4. If security boundary changes, route security reviewer on strong model.
5. If cost budget low, split task and use Haiku for discovery.
6. If model confidence low, run one cheap scout before expensive synthesis.
7. If code edits are required, do not use low-capability model for final patch.
8. If review finds critical risk, escalate model.
9. If task is repetitive and bounded, batch on cheaper model.
10. If user explicitly asks maximum quality, prioritize Opus.

## Context window management

1. Track remaining window mentally after large file reads.
2. Summarize before broad implementation.
3. Keep a short active facts list.
4. Split unrelated work into separate agents.
5. Avoid pasting long generated artifacts into chat.
6. Use files for generated outputs, not conversation text.
7. Prefer structured JSON summaries from agents.
8. Compress old logs into command, exit code, key error.
9. Archive completed decisions in task state.
10. Stop and re-plan before last context segment.

## Chunking

1. Chunk by subsystem, not arbitrary line count.
2. Give each chunk a clear question.
3. Keep shared contract in every chunk prompt.
4. Avoid asking every chunk to solve whole task.
5. Merge chunk findings with deduplication.
6. Verify cross-file assumptions after merge.
7. Run final reviewer over changed diff.
8. Do not chunk tiny files.
9. Do not split strongly coupled functions.
10. Prefer one owner for final synthesis.

## Summarization

1. Summarize facts, not speculation.
2. Include file and line when known.
3. Include commands and outcomes.
4. Include unresolved questions.
5. Include decisions and reasons.
6. Exclude raw stack trace unless needed.
7. Exclude repeated examples.
8. Exclude style commentary.
9. Exclude agent self-description.
10. Keep under 200 words for handoff unless task requires more.

## Cost-aware execution

1. Estimate whether task needs exploration, coding, validation, or review.
2. Use cheap search before expensive reasoning.
3. Avoid parallel agents for tiny tasks.
4. Use parallel agents for independent high-value checks.
5. Stop failed branch early when evidence disproves it.
6. Reuse previous tool output instead of rerunning.
7. Run targeted tests before full suite.
8. Run full validation once near completion.
9. Do not use web search when local docs answer.
10. Do not use docs lookup for general programming concepts.

## Agent budget rules

1. One planner for complex feature planning.
2. One TDD guide for new behavior.
3. One code reviewer after edits.
4. One language reviewer for changed language files.
5. One security reviewer for hooks/files/subprocess/network.
6. Avoid duplicate agents with same prompt.
7. Run independent reviewers in parallel.
8. Keep prompts self-contained but short.
9. Ask agents for findings, not essays.
10. Verify agent findings before reporting done.

## Tool output control

1. Use Read only for needed ranges.
2. Use Grep with head limits.
3. Use Glob over shell find.
4. Use Bash only for commands that need shell.
5. Prefer JSON output from project CLIs.
6. Avoid verbose test output unless failing.
7. Save large reports to files if user asks.
8. Do not print huge diffs in final response.
9. Keep final summary to changed files and validation.
10. Mention unrun checks explicitly.

## Token waste patterns

1. Rereading same file after Edit.
2. Running full suite repeatedly before targeted tests pass.
3. Spawning agents for single-file obvious fix.
4. Asking docs for APIs not used.
5. Searching whole repo for known path.
6. Pasting full logs into prompt.
7. Asking broad “review everything” without scope.
8. Keeping stale plan text in active prompt.
9. Summarizing every tool result in detail.
10. Recomputing git state without need.

## Token-saving patterns

1. Use exact filenames.
2. Use exact command failures.
3. Use structured asks.
4. Use targeted line reads.
5. Use concise agent prompts.
6. Use deterministic tests.
7. Use local caches.
8. Use short handoff summaries.
9. Use command JSON mode.
10. Use explicit stop criteria.

## Prompt compression examples

Original:

“Can you please take a look at the session tool and see why it might not be working? I ran some stuff and it failed, maybe around CSV export, and I need it fixed comprehensively with tests.”

Slim:

“Fix `tools/vex_sessions.py export --format csv`. Test `tests/test_vex_sessions.py::test_export_csv_outputs_rows` fails. Keep stdlib only. Run targeted test.”

Original:

“I want to improve token usage across our agent harness because sometimes it reads too much context and uses expensive models.”

Slim:

“Add token optimization guidance: prompt slimming, model routing, context chunking, cost-aware execution. Include CLI commands and validation.”

## Review checklist

- Prompt has one primary task.
- Prompt names scope.
- Prompt keeps safety constraints.
- Prompt includes exact failure evidence.
- Prompt defines output shape.
- Prompt excludes irrelevant history.
- Model choice matches task type.
- Agent fan-out has unique roles.
- Context reads are narrow.
- Validation is targeted first.

## CLI workflow

1. Run `python tools/vex_optimize.py analyze`.
2. Review session totals and hotspots.
3. Run `python tools/vex_optimize.py suggest --task "..."`.
4. Slim prompt with `python tools/vex_optimize.py slim "..."`.
5. Apply model recommendation.
6. Run targeted work.
7. Re-check totals after session recording.

## Safe defaults

- Never drop security constraints.
- Never drop exact error messages.
- Never drop user acceptance criteria.
- Never downgrade model for high-risk security work.
- Never compress away file paths needed for patching.
- Never replace validation with confidence.

## Output guidance

For user-facing output, report:

1. Main optimization found.
2. Exact change suggested.
3. Expected token or cost effect when measurable.
4. Risk if any.
5. Next command.

## Integration with continuous learning

1. Session store records usage.
2. Instinct system finds repeated waste.
3. Token optimizer suggests route changes.
4. High-confidence patterns become rules.
5. Human review stays required for promotion.

## Anti-patterns

- “Summarize everything” without audience.
- “Review whole repo” without risk area.
- “Use best model always” for trivial work.
- “Use cheapest model always” for hard decisions.
- “Read all docs” before knowing API needed.
- “Keep all context just in case.”
- “Run all tests after every edit.”
- “Spawn many agents for same viewpoint.”
- “Paste entire files into final answer.”
- “Hide unvalidated assumptions.”

## Final rule

Token optimization is not about making prompts tiny. It is about preserving the load-bearing facts and deleting everything else.
