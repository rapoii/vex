---
name: writing-skills
description: Guide for writing high-quality SKILL.md files for VEX. Use this skill when creating or updating skill definitions to ensure they meet the Superpowers methodology standards.
author: Rafi Permana
version: 1.0.0
tags: [meta, documentation, guide, vex, superpowers]
---

# Writing Excellent SKILL.md Files

This skill provides the definitive guide on creating high-quality, effective `SKILL.md` files within the Vareva ECC Extended (VEX) ecosystem. A well-written skill definition is the difference between an AI assistant that guesses and one that executes with precision.

## When to Activate

Activate this skill when:
- Creating a new `SKILL.md` file from scratch
- Refactoring or updating an existing skill
- Reviewing a pull request that adds or modifies a skill
- Training team members on how to contribute to the VEX ecosystem
- You are unsure why an existing skill is not triggering or behaving correctly

## Core Philosophy: The Superpowers Methodology

The Superpowers methodology treats AI assistants not as chatty helpers, but as deterministic function executors. A skill is a contract: "When you see X, execute steps Y, and verify with Z."

Good skills are:
1. **Trigger-focused**: They define exactly *when* the AI should wake up.
2. **Deterministic**: They provide step-by-step instructions, removing AI guesswork.
3. **Opinionated**: They dictate the *right* way to do things in your specific architecture.
4. **Verifiable**: They include concrete steps to prove the task was done correctly.

## Required Sections

Every `SKILL.md` file must include the following sections, in this order:

### 1. YAML Frontmatter
Contains metadata used by the VEX harness to parse and index the skill.
```yaml
---
name: your-skill-name
description: A 1-2 sentence summary of what this does.
author: Your Name
version: 1.0.0
tags: [tag1, tag2, tag3]
---
```

### 2. Title and Description
A human-readable `H1` title and a brief overview of the skill's purpose.

### 3. When to Activate (The Triggers)
This is the most critical section. If the AI doesn't know when to use the skill, the skill is useless. Provide specific, literal examples of user prompts or codebase states that should trigger the skill.

**Good:**
- "Activate when the user says: 'Create a new feature', 'Add a new route', or 'Implement [X] feature'."
- "Activate when you see an error related to `PrismaClientKnownRequestError`."
- "Activate when modifying any file in the `src/auth/` directory."

**Bad:**
- "Use this for development."
- "When the user wants help with the database."

### 4. How It Works (The Execution Steps)
Break down the task into a numbered list of concrete actions. Use imperative verbs.

**Good:**
1. Check if the branch is clean using `git status`.
2. Run the `npm run test` command.
3. If tests pass, create a commit with the prefix `feat:`.

**Bad:**
- "Make sure everything is okay before committing."
- "Write the code."

### 5. Examples (The Code)
Provide concrete code snippets showing the *expected output* or the *pattern to follow*. Do not rely on the AI's internal knowledge of a framework; show it your exact architectural preferences.

### 6. Pitfalls / Common Mistakes
Tell the AI what *not* to do. LLMs have common failure modes; document them here to preempt them.

**Good:**
- "Do not use `any` in TypeScript. Use `unknown` if the type is truly dynamic."
- "Never mutate the Redux state directly. Always return a new state object."

### 7. Verification / Quality Checklist
How does the AI prove it finished the job?

**Good:**
- "Run `npm run build` and ensure there are zero errors."
- "Verify that the new endpoint returns a 200 OK status code using `curl`."

## Examples of Great Skill Writing

### Example: Trigger Definition
```markdown
## When to Activate

Trigger this skill unconditionally when:
- The user prompt contains the words "migrate", "database change", or "schema update".
- The user asks to "add a column", "drop a table", or "change a relationship".
- You are modifying `schema.prisma`.
```

### Example: Execution Steps
```markdown
## How It Works

1. **Analyze**: Read the current `schema.prisma` file to understand the existing state.
2. **Modify**: Apply the user's requested changes to `schema.prisma`. Follow the naming conventions defined in `rules/database.md`.
3. **Format**: Run `npx prisma format` to ensure consistent styling.
4. **Generate**: Run `npx prisma generate` to update the Prisma Client.
5. **Migrate**: Run `npx prisma migrate dev --name <descriptive_name>` to create the migration file.
```

## Quality Checklist

Before submitting a new `SKILL.md` file, verify it against this checklist:

- [ ] Does it have valid YAML frontmatter?
- [ ] Are the triggers specific and realistic? (Would a user actually type that?)
- [ ] Are the execution steps deterministic? (Can a junior developer follow them without asking questions?)
- [ ] Are there concrete code examples demonstrating the preferred pattern?
- [ ] Is there a verification step to ensure the task was completed successfully?
- [ ] Did you avoid generic boilerplate ("Sure, I can help with that")?
- [ ] Is the skill scoped to a specific task, rather than a broad, vague domain?

## Common Mistakes to Avoid

1. **The "Everything" Skill**: Don't write a single skill that tries to handle frontend, backend, and DevOps. Split it into `frontend-feature`, `backend-api`, and `deploy-service`.
2. **Assuming LLM Knowledge**: Don't say "Write a React component". Say "Write a React functional component using Tailwind CSS for styling and `lucide-react` for icons, following the pattern in `components/ui/button.tsx`."
3. **Missing Verification**: If a skill doesn't end with a test, build, or validation step, it's incomplete.
4. **Fluff Words**: Avoid words like "carefully", "robust", "scalable", or "best practices". Replace them with concrete rules (e.g., instead of "write scalable code", write "Extract reusable logic into custom hooks in the `src/hooks` directory").
5. **Template Boilerplate**: Do not leave placeholder text like `[Insert Trigger Here]` in the final file.

## Advanced: Chaining Skills

You can instruct a skill to invoke other skills or agents. For example:

```markdown
## Next Steps
After completing this skill, invoke the `security-review` agent to analyze the new code for vulnerabilities before committing.
```

This creates powerful, automated workflows that mirror human engineering processes.
