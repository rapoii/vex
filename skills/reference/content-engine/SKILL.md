---
name: content-engine
description: Content generation workflow for blogs, tutorials, documentation, and changelogs.
---

# Content Engine

Use this skill to plan, generate, review, and publish technical content consistently.

Goal: produce useful content with repeatable workflow and stable voice.

## Content types

VEX content commonly falls into four types:

1. Blog
2. Tutorial
3. Documentation
4. Changelog

Each type has different purpose, structure, and review criteria.

## Blog

Purpose: explain idea, decision, pattern, or story.

Good for:

- Announcing concepts.
- Explaining engineering decisions.
- Comparing approaches.
- Teaching mental models.
- Sharing lessons from incidents or builds.

Blog structure:

1. Hook.
2. Context.
3. Main argument.
4. Evidence or examples.
5. Tradeoffs.
6. Conclusion and next action.

Blog checklist:

- Strong point of view.
- Concrete examples.
- Clear audience.
- Honest limitations.
- Search-friendly title.
- No unsupported hype.

## Tutorial

Purpose: help reader complete task.

Good for:

- Installing tool.
- Building feature.
- Running workflow.
- Creating skill.
- Configuring hook.
- Migrating setup.

Tutorial structure:

1. Outcome.
2. Prerequisites.
3. Setup.
4. Step-by-step instructions.
5. Verification.
6. Troubleshooting.
7. Next steps.

Tutorial checklist:

- Commands copyable.
- Each step has expected result.
- No hidden prerequisites.
- Failure cases covered.
- Screenshots or outputs when useful.
- Final verification included.

## Documentation

Purpose: be accurate reference for behavior.

Good for:

- APIs.
- Commands.
- Config fields.
- File formats.
- Architecture contracts.
- Skill authoring rules.

Documentation structure:

1. What it is.
2. When to use.
3. Syntax or schema.
4. Options.
5. Examples.
6. Errors.
7. Related references.

Documentation checklist:

- Matches current behavior.
- Complete required fields.
- Optional fields marked.
- Defaults stated.
- Examples minimal and realistic.
- Edge cases documented.
- No invented behavior.

## Changelog

Purpose: tell users what changed and what action is needed.

Good for:

- Releases.
- Breaking changes.
- New skills.
- Bug fixes.
- Security fixes.
- Deprecations.

Changelog structure:

1. Version and date.
2. Highlights.
3. Added.
4. Changed.
5. Fixed.
6. Removed or deprecated.
7. Migration notes.

Changelog checklist:

- User impact first.
- Breaking changes explicit.
- Migration steps included.
- Internal-only details omitted.
- Security fixes described without exploit detail.
- Links to docs or PRs when useful.

## Workflow

Use five-stage workflow:

1. Research
2. Outline
3. Draft
4. Review
5. Publish

Do not skip review for user-facing content.

## Stage 1: Research

Purpose: collect facts before writing.

Research inputs:

- Source code.
- README and docs.
- Existing skills.
- Issues or PRs.
- Official library docs.
- Release notes.
- User feedback.
- Error reports.
- Benchmarks or measurements.

Research questions:

- Who is reader?
- What problem do they have?
- What should they do after reading?
- What facts must be exact?
- What examples prove claims?
- What changed recently?
- What must not be promised?

Research rules:

- Verify current behavior from repo when possible.
- Use official docs for library/API claims.
- Keep source links for claims.
- Separate facts from assumptions.
- Do not include private or sensitive data.

Research output:

```text
Audience:
Goal:
Key facts:
Examples:
Risks:
Sources:
```

## Stage 2: Outline

Purpose: design shape before prose.

Outline should include:

- Working title.
- Reader promise.
- Section headers.
- Key points per section.
- Examples needed.
- Verification or source needed.
- Call to action.

Blog outline example:

```text
Title: Systematic Debugging for Agent Harnesses
Promise: Learn four-phase workflow for root-cause fixes.
Sections:
- Why patch-first debugging fails
- Phase 1: reproduce
- Phase 2: isolate
- Phase 3: identify
- Phase 4: fix with guardrails
- Checklist
CTA: Use skill for next unclear bug.
```

Tutorial outline example:

```text
Title: Create a VEX Skill
Promise: Build reusable skill with manifest-friendly structure.
Sections:
- Prerequisites
- Create directory
- Write SKILL.md
- Add examples
- Validate pack
- Use skill in Claude Code
CTA: Add tests for generated packs.
```

## Stage 3: Draft

Purpose: produce complete content quickly while preserving structure.

Draft rules:

- Write for stated audience.
- Start with concrete problem.
- Use active voice.
- Keep paragraphs short.
- Use examples early.
- Put commands in code blocks.
- Mark placeholders clearly if facts missing.
- Avoid filler.
- Avoid unsupported claims.
- Avoid marketing voice unless content type requires launch copy.

For technical content:

- Include exact filenames when relevant.
- Include exact commands when relevant.
- Include expected output or success signal.
- Include errors and remediation.
- Include tradeoffs.

## Stage 4: Review

Purpose: catch inaccuracies, gaps, and style drift.

Review dimensions:

### Accuracy

- Does content match repo behavior?
- Are commands valid?
- Are config names exact?
- Are versions current?
- Are examples runnable?
- Are limitations stated?

### Usefulness

- Can reader complete task?
- Are prerequisites clear?
- Are next steps obvious?
- Are common failures covered?
- Is article too broad?

### Structure

- Does hook work?
- Does section order make sense?
- Are headings specific?
- Are lists scan-friendly?
- Is conclusion actionable?

### Style

- Is tone consistent?
- Are terms consistent?
- Are sentences direct?
- Is filler removed?
- Are claims grounded?

### Safety

- No secrets.
- No private URLs unless authorized.
- No destructive command without warning.
- No exploit details beyond defensive need.
- No license-incompatible content copied.

Review output:

```text
Ready: yes/no
Blockers:
Fixes:
Optional improvements:
```

## Stage 5: Publish

Purpose: deliver content in correct format and location.

Publish checklist:

- File path correct.
- Frontmatter valid if used.
- Title matches index/link.
- Internal links work.
- Images have alt text.
- Code blocks use language tags.
- Generated output stable.
- Spellcheck or lint if available.
- Preview rendered page if possible.

Post-publish:

- Note migration actions if changelog.
- Update index if docs require it.
- Share summary with audience.
- Track feedback.

## Tone and style consistency

Consistency matters across content pack.

Define voice:

- Practical.
- Direct.
- Engineering-first.
- Evidence-based.
- Free-forever aligned.
- No paid dependency push.
- No demo-only framing.

Style rules:

- Prefer short sentences.
- Use same term for same concept.
- Prefer concrete examples.
- Explain tradeoffs honestly.
- Avoid hype words.
- Avoid vague claims like "powerful" without proof.
- Avoid jokes that age poorly.

Term consistency examples:

- Use "skill" for reusable workflow docs.
- Use "agent" for role-specific subagent definitions.
- Use "hook" for event-triggered commands.
- Use "command" for slash-command entrypoints.
- Use "profile" for install profile.
- Use "manifest" for source-of-truth config.

## Content quality gates

Before calling content done:

- Reader goal is explicit.
- First paragraph contains problem.
- Every section supports goal.
- Examples are relevant.
- Commands are checked or marked unverified.
- SEO title and description exist when public web content.
- Content avoids invented capabilities.
- Content states limitations.
- Content has clear next action.

## Repurposing content

One source can become multiple outputs:

- Blog → tutorial checklist.
- Tutorial → docs reference.
- Changelog → release announcement.
- Docs → video script.
- Video script → article summary.

When repurposing:

- Change structure for medium.
- Keep facts consistent.
- Remove medium-specific assumptions.
- Re-check examples.
- Preserve source links.

## Common failure modes

Avoid:

- Writing before researching.
- Mixing tutorial and reference in confusing way.
- Claiming future features as current behavior.
- Publishing commands that were never run.
- Overloading article with every detail.
- Using inconsistent names for same object.
- Hiding limitations.
- Making changelog about internal implementation instead of user impact.

## Quick content brief

```text
Type:
Audience:
Goal:
Key message:
Required facts:
Examples:
Tone:
SEO target:
Publish location:
Review needs:
```
