---
name: article-writing
description: Technical article writing patterns for structure, examples, formatting, and SEO.
---

# Article Writing

Use this skill to draft, revise, or review technical articles.

Goal: make reader understand, trust, and act.

## Core structure

Technical articles usually follow:

1. Hook
2. Context
3. Body
4. Conclusion

This structure keeps article useful even when topic is complex.

## Hook

Purpose: earn attention quickly.

Good hooks:

- State concrete problem.
- Name audience pain.
- Show surprising result.
- Promise specific outcome.
- Start with small story from real engineering work.
- Compare bad path and better path.

Weak hooks:

- Generic history.
- Broad definitions everyone knows.
- Marketing claims.
- Vague statements like "software is changing fast".
- Long preambles before problem appears.

Hook examples:

```text
Bad: Testing is important for modern software teams.
Good: A test that passes while production fails is worse than no test because it trains team to trust wrong signal.
```

```text
Bad: In this article, we will discuss debugging.
Good: Most debugging time is wasted before first useful experiment. Four phases prevent that waste.
```

## Context

Purpose: orient reader before deep detail.

Include:

- What system or concept article covers.
- Why problem matters.
- What reader should already know.
- What article will and will not cover.
- Constraints that shape solution.

Keep context short. Reader came for solution.

Context checklist:

- Audience named or implied.
- Problem framed in practical terms.
- Terms defined if ambiguous.
- Scope boundaries explicit.
- Outcome clear.

Example:

```text
This guide is for engineers building local agent harnesses. It focuses on reproducible skill packs, not hosted orchestration platforms.
```

## Body

Purpose: teach through sequence.

Common body patterns:

### Problem → diagnosis → solution

Best for bug stories, debugging guides, migration notes.

1. Show failure.
2. Explain why obvious fix fails.
3. Identify cause.
4. Apply fix.
5. Verify result.

### Concept → example → variation

Best for explaining APIs, patterns, and architecture.

1. Define idea.
2. Show minimal example.
3. Show realistic example.
4. Show edge cases.
5. Show tradeoffs.

### Step-by-step tutorial

Best for task completion.

1. Prerequisites.
2. Setup.
3. First working result.
4. Add real-world constraint.
5. Validate output.
6. Next steps.

### Decision guide

Best for comparing tools or approaches.

1. State decision.
2. Explain options.
3. Compare tradeoffs.
4. Recommend default.
5. Explain when default changes.

## Code examples: show, don't tell

Code should prove claims.

Good code examples:

- Compile or run if possible.
- Include necessary imports when helpful.
- Use meaningful names.
- Show input and output.
- Focus on one idea.
- Avoid fake complexity.
- Avoid unrelated architecture.

Bad code examples:

- Pseudocode pretending to be real.
- Missing key setup.
- Generic names like foo and bar.
- Huge blocks with tiny relevant line.
- Comments explaining every line.
- Examples that require hidden context.

### Minimal example pattern

```ts
const sorted = [...files].sort((a, b) => a.path.localeCompare(b.path));
```

Then explain why it matters:

```text
Stable sorting makes generated output reproducible across filesystems.
```

### Before/after pattern

Use when article teaches fix.

```ts
// Before
for (const file of files) {
  render(file);
}

// After
for (const file of [...files].sort((a, b) => a.path.localeCompare(b.path))) {
  render(file);
}
```

Keep before/after small. If full diff is needed, link or append.

### Command examples

Commands should be copyable:

```bash
npm test -- --runInBand
```

Include expected signal:

```text
Expected: regression test fails before fix and passes after fix.
```

### Error examples

Show exact error when important:

```text
Error: manifest entry missing required field "description"
```

Then decode it:

```text
This means schema validation failed before adapter generation.
```

## Formatting

Formatting makes article scannable.

Use:

- H2 for major sections.
- H3 for subpatterns.
- Short paragraphs.
- Bullets for lists.
- Numbered lists for ordered steps.
- Tables for comparisons.
- Code blocks for code and commands.
- Callouts sparingly.
- Images when visual structure matters.

Avoid:

- Deep heading nests.
- Long walls of text.
- Multiple ideas in one paragraph.
- Tables with huge prose cells.
- Decorative images.
- Excess bold text.

## Headers

Headers should describe value.

Weak:

```text
Introduction
Details
More info
Conclusion
```

Better:

```text
Why flaky reproduction blocks root-cause fixes
Shrink failing input before editing code
Add guardrails where invariant breaks
```

Header checklist:

- Specific.
- Search-friendly.
- Useful in table of contents.
- Not too clever.
- Matches section content.

## Lists

Use bullets when order does not matter.

Use numbered lists when order matters.

Good bullet list:

- Exact command.
- Exit code.
- stdout.
- stderr.
- Files changed.

Good numbered list:

1. Reproduce failure.
2. Shrink input.
3. Identify root cause.
4. Add regression test.
5. Fix code.
6. Verify original repro.

## Images and diagrams

Use images when they reduce explanation.

Good image uses:

- Architecture flow.
- UI state before/after.
- Timeline of race condition.
- Data transformation pipeline.
- Visual output comparison.

Bad image uses:

- Screenshot of code instead of code block.
- Decorative hero image.
- Diagram with unreadable labels.
- Image that repeats text exactly.

Image checklist:

- Alt text describes meaning.
- Caption explains takeaway.
- Text remains understandable without image.
- Sensitive data removed.
- Resolution readable on mobile.

## SEO considerations

SEO helps right readers find article. Do not damage usefulness for keywords.

### Search intent

Identify intent:

- Learn concept.
- Fix error.
- Compare tools.
- Complete task.
- Decide architecture.

Match structure to intent.

Examples:

- "how to debug flaky tests" wants workflow and checklist.
- "TypeError cannot read property map" wants cause and fix.
- "Remotion vs Manim" wants comparison and recommendation.

### Title

Good technical title:

- Names topic.
- Names outcome.
- Stays specific.
- Avoids clickbait.

Examples:

```text
Systematic Debugging: Four Phases for Root-Cause Fixes
```

```text
How to Write Reproducible Code Generators with Stable Output
```

### Meta description

Write one sentence:

- Problem.
- Solution.
- Audience.

Example:

```text
A practical debugging workflow for engineers who need reliable reproduction, isolation, root-cause analysis, and regression guardrails.
```

### Keywords

Use natural terms:

- In title if accurate.
- In first paragraph.
- In headers where useful.
- In alt text only when image shows topic.

Avoid keyword stuffing.

### Internal links

Link to related articles when they help next step:

- Debugging guide → testing guide.
- Agent guide → hook guide.
- Install guide → troubleshooting guide.

Use descriptive anchor text:

```text
Use the strict TDD workflow for behavior changes.
```

Avoid:

```text
Click here.
```

## Voice and style

Prefer:

- Concrete nouns.
- Active verbs.
- Short sentences.
- Practical examples.
- Honest tradeoffs.
- Clear recommendations.

Avoid:

- Hype.
- Empty adjectives.
- Passive fog.
- Unqualified absolutes.
- Insider jokes.
- Overexplaining basics.

## Technical accuracy

Before publishing:

- Run code examples when possible.
- Verify command syntax.
- Check version-specific behavior.
- Mark assumptions.
- Avoid claiming benchmarks without data.
- Avoid security advice without current evidence.
- Link official docs for APIs.

## Conclusion

Conclusion should not summarize every section mechanically.

Good conclusion:

- Restate main takeaway.
- Give next action.
- Mention tradeoff or limit.
- Link next useful resource.

Example:

```text
Root-cause debugging is slower for first ten minutes and faster for rest of incident. Start with reproduction, shrink the failing case, prove cause, then add guardrail where invariant broke.
```

## Revision checklist

- Hook states concrete problem.
- Context is short.
- Body follows clear pattern.
- Examples run or are marked conceptual.
- Headers scan well.
- Formatting supports skimming.
- SEO terms match search intent.
- Claims have evidence.
- Conclusion gives next action.
- No filler remains.
