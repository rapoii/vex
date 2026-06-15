---
name: token-budget-advisor
description: Estimate token cost, context pressure, and agent fan-out before large LLM tasks.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: optimization
  triggers: ["Large prompt/workflow", "Many agents", "Cost-sensitive run"]
---

# Token Budget Advisor

Guidelines for managing LLM context windows, reducing token costs, and optimizing agent workflows.

## When to Activate

- Planning complex multi-agent workflows.
- Executing tasks on very large codebases.
- Debugging context limit errors.
- Optimizing cost-sensitive operations.

## Core Strategies

### 1. Context Window Management
The LLM's context window is precious. Do not fill it with irrelevant data.

- **Filter Before Sending**: Use `grep` or specific `read` limits rather than dumping entire files into the context.
- **Summary Abstractions**: Instead of reading 10 full files, read their interfaces or summaries to decide which ones matter.
- **Clear the Context**: If a conversation gets too long and confused, summarize the current state and start a fresh session or agent task.

### 2. Agent Fan-Out Optimization
When orchestrating multiple agents, control the fan-out to prevent exponential token explosion.

- **Batching**: Instead of spawning 50 agents for 50 files, spawn 5 agents, each handling 10 files.
- **Early Exit**: If an agent is searching for a condition and finds it, terminate the search immediately rather than letting all agents finish.
- **Hierarchical Delegation**: A planner agent creates tasks -> Worker agents execute tasks -> Reviewer agent checks results. Don't let all agents talk to all other agents.

### 3. Output Token Minimization
Output tokens are often more expensive and slower to generate than input tokens.

- **Request Diff Formats**: Ask for patch formats or search/replace blocks instead of asking the LLM to rewrite the entire 500-line file.
- **Structured Output**: Use JSON or YAML constraints to prevent the model from generating long, unnecessary conversational preambles.
- **Stop Sequences**: Define stop sequences if you only need a specific part of an answer.

## Example: Optimizing a File Search

**Bad (High Token Cost):**
"Read all files in `src/` and tell me which ones use the database."
*(This loads the entire `src/` directory into context).*

**Good (Low Token Cost):**
1. Use `grep -l "import.*db" src/**/*.ts` to find the filenames.
2. Only pass those specific filenames to the LLM for deeper analysis if needed.

## Estimating Costs

Before running a large workflow, estimate the cost:
1. Average tokens per file (e.g., 500 lines ~ 3000 tokens).
2. Number of files involved.
3. Number of agent iterations.
4. Compare against model pricing (e.g., Opus vs. Sonnet vs. Haiku).

Use smaller models (like Haiku) for simple classification, routing, or basic extraction tasks. Reserve large models (like Opus) for complex synthesis or architecture design.
