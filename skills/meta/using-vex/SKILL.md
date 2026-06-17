---
name: using-vex
description: VEX onboarding guide covering install profiles, agents, skills, hooks, commands, config, and troubleshooting.
---

# Using VEX

Use this skill when onboarding to VEX or explaining how to use VEX packs in Claude Code and compatible harnesses.

VEX means Vareva ECC Extended.

VEX is a free MIT-licensed agent harness system. It packages agents, skills, hooks, commands, rules, contexts, and config into reusable packs.

Primary target: Claude Code.

Secondary target: harness-neutral abstractions for future adapters.

## What VEX provides

VEX provides reusable operational knowledge:

- Agents for role-specific work.
- Skills for repeatable workflows.
- Hooks for automated guardrails.
- Commands for user-invoked actions.
- Rules for always-on behavior.
- Contexts for scoped memory or background.
- Config manifests for source of truth.
- Install profiles for different usage levels.
- Validation scripts for pack quality.

VEX is not a hosted SaaS requirement. Core must remain free and MIT-compatible.

## Mental model

Think of VEX as layered harness content:

1. Source manifests define what exists.
2. Adapters translate manifests into harness-specific files.
3. Installers copy or patch files after confirmation.
4. Hooks and commands run inside user harness.
5. Validators check structure before release.

Claude Code adapter comes first.

Harness-neutral format comes next.

Dashboard and advanced automation come after core packs work.

## Project layout

Common VEX directories:

```text
agents/      Agent definitions
skills/      Reusable workflows
commands/    Slash commands and command metadata
rules/       Always-on project and harness rules
hooks/       Hook definitions and templates
contexts/    Context templates and memory scopes
config/      Manifests, schemas, defaults
tools/       TypeScript and Python implementation code
scripts/     Validation, packaging, release helpers
```

## Installation overview

VEX installs through scripts and profiles.

Typical installer:

```bash
./install.sh
```

Profiles let user choose scope.

Common profile ideas:

- Minimal: core rules and essential skills.
- Developer: agents, skills, commands, hooks.
- Full: broad pack with references and workflows.
- CI: validation-only or noninteractive checks.
- Custom: explicit selected components.

Exact profile names must come from repo config or installer help.

Check installer options:

```bash
./install.sh --help
```

Use dry-run before writes when available:

```bash
./install.sh --dry-run
```

Use profile when supported:

```bash
./install.sh --profile developer --dry-run
```

Do not assume installer overwrites files. VEX installers should avoid destructive behavior and require explicit confirmation before patching or replacing user files.

## Installation safety

Before install:

- Review selected profile.
- Run dry-run.
- Check target paths.
- Confirm files to create, patch, or skip.
- Back up custom local harness config if needed.

Installer should:

- Validate inputs.
- Show planned operations.
- Avoid destructive writes by default.
- Preserve user files.
- Support dry-run.
- Produce clear errors.

If installer wants to overwrite or delete, stop and ask for explicit confirmation.

## Using agents

Agents are specialized role definitions.

Use agents when work benefits from focused expertise or parallel review.

Examples:

- code-reviewer: review diffs for correctness.
- security-reviewer: inspect security-sensitive changes.
- typescript-reviewer: review TypeScript and JavaScript.
- build-error-resolver: fix build/type/lint failures.
- architect: design system interfaces.
- accessibility: inspect WCAG and keyboard behavior.

Good agent use:

- Give self-contained prompt.
- State exact goal.
- State files or scope.
- State whether agent may edit.
- Ask for concise output.
- Verify edits afterward.

Bad agent use:

- Delegate vague responsibility.
- Ask agent to decide product requirements.
- Spawn agents for trivial one-line tasks.
- Duplicate same search in main context and agent.
- Trust agent summary without checking changed files.

Agent prompt template:

```text
Review current diff for correctness issues only. Focus on validators and installers. Do not edit files. Report severity, file, line, and concrete fix.
```

## Using skills

Skills are reusable workflows stored under `skills/`.

A skill usually has:

- Name.
- Description.
- Trigger guidance.
- Step-by-step method.
- Checklists.
- Output format.

Use skills when task matches workflow:

- Debugging unclear bug.
- Planning implementation.
- Running TDD.
- Reviewing code.
- Generating docs.
- Shipping release.

Skill files are markdown and should be practical. They are not marketing pages.

Good skill traits:

- Clear when to use.
- Clear exit criteria.
- Specific commands or checks when possible.
- Safety notes for risky work.
- Minimal assumptions.
- Reusable across projects.

## Using hooks

Hooks are automated commands triggered by harness events.

Use hooks for guardrails:

- Format or lint checks.
- Prevent secret commits.
- Validate generated files.
- Block destructive commands.
- Remind about tests.
- Enforce output size limits.

Hooks must be safe.

Hook rules:

- Validate external input.
- Avoid destructive behavior.
- Keep output concise.
- Fail clearly.
- Work without external credentials.
- Avoid telemetry by default.
- Handle Windows and POSIX when intended.
- Avoid leaking secrets.

Hook testing should cover:

- Allowed input.
- Blocked input.
- Malformed input.
- Large input.
- Missing files.
- Exit codes.
- stdout and stderr.

## Using commands

Commands are user-invoked slash-command style workflows.

Use commands when user needs named action:

- Review branch.
- Run validation.
- Prepare release.
- Generate docs.
- Start debugging workflow.

Command metadata should define:

- Name.
- Description.
- Arguments.
- Required tools.
- Safety constraints.
- Expected output.

Good commands are predictable. They do not hide broad side effects.

## Configuration

VEX configuration lives under `config/`.

Config can include:

- Manifests.
- Schemas.
- Defaults.
- Profiles.
- Adapter mappings.
- Validation rules.

Manifests should be source of truth.

Prefer explicit manifests over hidden conventions.

Config principles:

- Human-readable.
- Validated by schema.
- Stable ordering.
- Reproducible generated output.
- No secrets committed.
- Defaults safe.
- Required fields explicit.

## Profiles

Profiles select subsets of VEX.

A profile may include:

- Agents.
- Skills.
- Commands.
- Hooks.
- Rules.
- Contexts.
- Settings.

Profile design rules:

- Minimal profile should be safe and small.
- Developer profile can include active workflows.
- CI profile should be noninteractive.
- Full profile can include references and optional packs.
- Custom profile should be explicit.

Profile validation should check:

- Referenced files exist.
- Required metadata exists.
- No duplicate names.
- Dependencies included.
- Incompatible items flagged.

## Environment variables

VEX may use env vars for installer behavior or adapter selection.

Env var rules:

- Document every supported variable.
- Provide defaults.
- Never require secrets for tests.
- Do not add telemetry by default.
- Validate values.
- Avoid env-only hidden behavior when manifest should own setting.

Possible env var categories:

- Install target.
- Profile selection.
- Noninteractive mode.
- Adapter selection.
- Debug logging.
- Validation strictness.

Exact names must come from current repo docs or installer help.

## Validation

Run validation before publishing VEX packs.

Validation should check:

- Required files exist.
- Skill frontmatter valid.
- Agent metadata valid.
- Commands have metadata.
- Hooks have tests or fixtures.
- Schemas match manifests.
- Generated files reproducible.
- License requirements satisfied.

Potential validation command:

```bash
npm test
```

or:

```bash
python scripts/validate.py
```

Use actual commands from package metadata or scripts directory.

## Working with generated files

Generated files must be reproducible.

Rules:

- Stable sort all generated lists.
- Avoid timestamps unless required.
- Avoid machine-specific paths.
- Normalize path separators.
- Keep source manifest authoritative.
- Include generator tests.

If generated output changes unexpectedly:

1. Check input manifest.
2. Check generator version.
3. Check filesystem ordering.
4. Check path normalization.
5. Re-run generation.
6. Compare diff.

## Troubleshooting install

### Installer command not found

Check:

- Current directory.
- Script exists.
- Execution permissions on POSIX.
- Shell type.

Try:

```bash
ls
```

```bash
./install.sh --help
```

On Windows, use documented Windows-compatible path if available.

### Profile not found

Check:

- Profile name spelling.
- Config manifest.
- Installer help.
- Whether profile belongs to adapter.

Run dry-run with known profile.

### Permission denied

Check:

- Target path ownership.
- File locks.
- Running editor or harness process.
- Corporate endpoint protection.

Do not use force delete. Identify holder or choose user-writable target.

### Existing file conflict

Expected safe behavior:

- Show conflict.
- Skip or patch only with confirmation.
- Preserve original content.
- Offer diff if possible.

If conflict appears, inspect file before approving overwrite.

### Hook fails after install

Check:

- Hook path exists.
- Runtime installed.
- Command works manually.
- Input JSON shape matches expected schema.
- Output is under harness limits.
- Exit code semantics.

Run hook fixture tests if available.

### Skill not available

Check:

- Skill installed in expected harness directory.
- `SKILL.md` exists.
- Frontmatter valid.
- Name unique.
- Harness restarted or reloaded if needed.

### Agent not available

Check:

- Agent file exists.
- Metadata valid.
- Tool list allowed by harness.
- Name does not collide.
- Installed profile includes agent.

### Command not available

Check:

- Command file exists.
- Metadata valid.
- Slash-command naming convention.
- Profile includes command.
- Harness reload completed.

## Troubleshooting validation

If validation fails:

1. Read first error.
2. Fix root cause, not all downstream symptoms.
3. Re-run focused validator.
4. Re-run full validation.
5. Check generated diff.

Common validation errors:

- Missing frontmatter.
- Duplicate names.
- Missing required description.
- Broken manifest reference.
- Invalid JSON/YAML.
- Non-reproducible output.
- License text mismatch.
- Hook fixture exit code mismatch.

## Safety and security

VEX touches harness behavior, so safety matters.

Security rules:

- Do not install secrets.
- Do not exfiltrate data.
- Do not add telemetry by default.
- Do not run destructive commands silently.
- Validate external input at boundaries.
- Keep tests free of external credentials.
- Keep generated files deterministic.
- Review hooks, installers, file writes, auth-like flows, and external calls.

Use security review for:

- Hooks.
- Installers.
- External network calls.
- File writes.
- Secret handling.
- Auth-like flows.
- Permission changes.

## Recommended workflows

### Adding a skill

1. Choose category under `skills/`.
2. Create directory.
3. Write `SKILL.md` with frontmatter.
4. Include when-to-use guidance.
5. Add concrete workflow.
6. Add checklists and output format.
7. Validate structure.
8. Review for clarity.

### Adding an agent

1. Define role and scope.
2. List allowed tools.
3. Add strong instructions.
4. Include when to use.
5. Keep role narrow.
6. Validate metadata.
7. Test with realistic prompt.

### Adding a hook

1. Define event and policy.
2. Write minimal script.
3. Validate input schema.
4. Add fixtures.
5. Test pass and fail.
6. Test malformed input.
7. Document install impact.
8. Security review.

### Adding command

1. Define user intent.
2. Define args.
3. Map to workflow.
4. Add safety checks.
5. Add output format.
6. Validate metadata.
7. Test invocation.

## Quality gates

Before VEX release or major pack update:

- Required files exist.
- MIT license names Rafi Permana and 2026.
- README explains install, features, comparison, roadmap.
- AGENTS.md explains orchestration and quality gates.
- SOUL.md guarantees free-forever philosophy.
- Package metadata exposes validation commands.
- Tests pass without external credentials.
- Installers support dry-run.
- Hooks are tested.
- Generated files are reproducible.

## Quick start checklist

```text
1. Read README.
2. Inspect install profiles.
3. Run installer dry-run.
4. Install chosen profile.
5. Reload harness if needed.
6. Confirm skills, agents, commands available.
7. Run validation.
8. Try one workflow.
```

## Help request template

When asking for help with VEX, include:

```text
Goal:
Command run:
Profile:
Adapter:
Expected:
Actual:
Error output:
OS/shell:
Files changed:
```

This makes debugging faster and prevents guessing.
