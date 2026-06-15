---
name: model-routing-optimizer
description: Route tasks to appropriate models by complexity, latency, cost, and risk.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: optimization
  triggers: ["Agent design", "Cost optimization", "Model choice"]
---

# Model Routing Optimizer

Strategy for selecting the right LLM model based on task complexity, cost, and speed requirements.

## When to Activate

- Designing multi-agent systems.
- Reducing API costs.
- Improving response latency in LLM workflows.

## The Model Tiers

### Tier 1: Heavyweight (e.g., Claude 3 Opus)
High capability, high reasoning, high cost, slow latency.

**Best for:**
- System architecture design.
- Solving complex, novel bugs.
- Synthesizing information across many diverse files.
- Evaluating the final output of other agents (Judge role).
- Initial task planning and decomposition.

### Tier 2: Midweight (e.g., Claude 3.5 Sonnet)
Strong coding capability, balanced cost and speed.

**Best for:**
- Writing actual code implementations.
- Refactoring existing files.
- Writing unit tests.
- General pair programming.
- The default choice for most development tasks.

### Tier 3: Lightweight (e.g., Claude 3 Haiku)
Very fast, very cheap, lower reasoning capability.

**Best for:**
- File classification and routing (e.g., "Is this file a React component?").
- Data extraction (e.g., "Extract all API endpoints from this file").
- Simple text transformations (e.g., converting JSON to YAML).
- Summarization of individual files.
- Basic linting or formatting checks.

## Routing Logic (Decision Tree)

When designing an automated workflow or agent system, use this logic:

1. **Does the task require deep reasoning or understanding of system architecture?**
   - Yes: Use Heavyweight (Opus).
2. **Does the task involve writing logic, algorithms, or complex code?**
   - Yes: Use Midweight (Sonnet).
3. **Is the task a simple classification, extraction, or translation?**
   - Yes: Use Lightweight (Haiku).
4. **Is the task highly repetitive and applied to hundreds of files?**
   - Yes: Force simplification of the prompt and use Lightweight (Haiku).

## Example Workflow (Bug Fix)

1. **Planner (Opus)**: Reads the bug report, analyzes the stack trace, and determines which files need to be investigated.
2. **Scanner (Haiku)**: Quickly scans 20 potential files to find where the specific variable is defined.
3. **Coder (Sonnet)**: Writes the patch for the 2 identified files and creates a test.
4. **Reviewer (Opus)**: Reviews the PR for edge cases and security implications before merge.

## Verification

- Monitor token usage and costs per workflow run.
- If a Lightweight model frequently fails a task, promote that task to a Midweight model.
- If a Heavyweight model is used for simple regex-like extraction, downgrade it to save costs and time.
