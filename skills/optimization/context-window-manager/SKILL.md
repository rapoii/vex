---
name: context-window-manager
description: Manage and optimize LLM context window usage through token estimation, semantic chunking, priority ranking, and payload summarization.
argument-hint: "[payload-type | optimization-strategy]"
metadata:
  origin: VEX
---

# Context Window Manager

Use this skill when building features that send large payloads to LLMs, to prevent exceeding context limits, reduce cost, and maintain retrieval accuracy (preventing "lost in the middle" phenomena).

## Triggers

- Generating prompts with large files, logs, or search results.
- Receiving "context window exceeded" or token limit errors.
- Implementing RAG (Retrieval-Augmented Generation) pipelines.
- Optimizing an agent's memory or transcript handling.
- Reviewing code that concatenates strings blindly into prompts.

## Inputs To Inspect

- Prompt construction logic (templates, string interpolation).
- Context gathering functions (file reading, DB queries, API fetches).
- Token counting libraries (`tiktoken`, `@anthropic-ai/tokenizer`).
- RAG chunking and embedding settings.

## Optimization Strategy

1. **Estimate**: Count tokens before sending. Reject or truncate early.
2. **Rank**: Sort context by relevance; drop the least relevant when near limits.
3. **Chunk**: Split large documents into logical sections, not arbitrary character counts.
4. **Compress**: Summarize old history or verbose logs before inclusion.
5. **Format**: Use XML tags structure to help the model navigate dense context efficiently.

## 1. Token Estimation

Never guess based on character count. Use the right tokenizer:

```typescript
// Node.js example using tiktoken (for OpenAI) or similar logic for Anthropic
import { get_encoding } from "tiktoken";

function isWithinBudget(text: string, limit: number): boolean {
  const enc = get_encoding("cl100k_base");
  const tokens = enc.encode(text);
  const count = tokens.length;
  enc.free();
  return count <= limit;
}
```
*Note: For Claude, 1 token ≈ 3.5 English characters.*

## 2. Priority Ranking & Truncation

Build context from highest priority to lowest, stopping when the budget is reached.

```python
def build_context(query, documents, max_tokens=8000):
    # Sort by relevance score (e.g., from vector DB)
    ranked_docs = sorted(documents, key=lambda x: x.score, reverse=True)
    
    context = []
    current_tokens = 0
    
    for doc in ranked_docs:
        doc_tokens = count_tokens(doc.content)
        if current_tokens + doc_tokens > max_tokens:
            break
            
        context.append(f"<document id=\"{doc.id}\">\n{doc.content}\n</document>")
        current_tokens += doc_tokens
        
    return "\n".join(context)
```

## 3. Semantic Chunking (RAG)

Do not split mid-sentence or mid-function.

- **Markdown**: Split by headers (`## `).
- **Code**: Split by AST (classes, functions).
- **Logs**: Keep stack traces intact; truncate repeating lines.

## 4. XML Tagging for Dense Context

Claude performs better with large context when it is clearly demarcated with XML tags.

```xml
<context>
  <file path="src/utils.ts">
    // content...
  </file>
  <file path="src/api.ts">
    // content...
  </file>
</context>
```

## 5. Log Compression Pattern

When piping raw logs or diffs, strip low-signal lines:

```bash
# Strip empty lines, comments, or debug noise before passing to LLM
cat app.log | grep -v "DEBUG" | tail -n 500 > compressed.log
```

## Common Pitfalls

- Blindly passing `file.read()` into a prompt without checking size.
- Pushing the context window to 100% capacity, leaving no tokens for the generated response.
- Assuming 1 word = 1 token (it's roughly 0.75 words per token for English, but much worse for code, JSON, or non-English text).
- Over-stuffing: providing 100k tokens of semi-relevant context degrades the model's ability to extract the exact answer.

## Done Criteria

- Context assembly enforces a strict maximum token budget.
- Payloads format multiple sources using clear XML boundaries.
- The most critical information is guaranteed to be included.
- Excess information is safely dropped or summarized without crashing the application.
