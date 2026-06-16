# VEX Fix Plan v5 — MEDIUM Priority Gaps

**Date:** 2026-06-16
**Source:** Gap analysis v ECC
**Status:** EXECUTING

---

## 11 MEDIUM Priority Gaps

### 1. Multi-model commands
- Create commands/multi-plan.md, multi-execute.md, multi-backend.md, multi-frontend.md, multi-workflow.md
- Slash commands for multi-model collaborative workflows

### 2. Selective install
- Update install.sh to support component selection
- `--components agents,skills,rules` (comma-separated)
- Install only listed components

### 3. Session adapters
- Enhance tools/vex_sessions.py with structured recording
- Record: tool calls, file changes, cost per session
- Export: JSON, CSV formats

### 4. Skill evolution
- Enhance tools/vex_instinct.py — evolve already done
- Add skill quality scoring based on usage data
- Auto-promote high-performing instincts to skills

### 5. Package manager detection
- Create tools/vex_detect.py — auto-detect package manager
- Detect: npm, pnpm, yarn, bun, pip, poetry, cargo, go mod
- Return: manager name, lockfile, install command

### 6. Orchestrator agents
- Create agents/core/orchestrator.md — complex multi-step workflow
- Create agents/core/orchestrator-backend.md — backend orchestration
- Create agents/core/orchestrator-frontend.md — frontend orchestration

### 7. Auto-format hooks
- Create hooks/scripts/auto-format.py — PostToolUse auto-format
- Detect file type, run appropriate formatter
- JS/TS: prettier, Python: black, Go: gofmt, Rust: rustfmt

### 8. Secret detection hooks
- Create hooks/scripts/secret-scanner.py — beforeSubmitPrompt
- Detect: sk-*, ghp_*, AKIA*, xoxb-*, -----BEGIN RSA PRIVATE KEY-----
- Block if secrets found in prompt

### 9. Session retention
- Add to tools/vex_sessions.py: auto-prune sessions older than N days
- Env var: VEX_SESSION_RETENTION_DAYS (default 30)
- CLI: `vex sessions prune [--days 30]`

### 10. Agent data home isolation
- Add VEX_AGENT_DATA_HOME env var support
- Isolate per-harness data (sessions, instincts, costs)
- Update tools to respect env var

### 11. Iterative retrieval pattern
- Create skills/optimization/iterative-retrieval/SKILL.md
- Progressive context refinement for subagents
- Chunk → retrieve → refine → repeat
- 100+ lines

---

## Execution

3 Claude Code workers:

| Worker | Tasks | Count |
|--------|-------|-------|
| **Commands+Install** | multi-model commands (5), selective install, package detection | 7 |
| **Hooks+Sessions** | auto-format, secret-scanner, session adapters, retention, data isolation | 5 |
| **Agents+Skills** | orchestrator agents (3), iterative-retrieval skill, skill evolution | 4 |

---

## Success Criteria

- [ ] 5 multi-model command .md files
- [ ] Selective install (--components flag)
- [ ] Package manager detection tool
- [ ] Auto-format hook script
- [ ] Secret scanner hook script
- [ ] Session adapters + retention
- [ ] Data home isolation
- [ ] 3 orchestrator agents
- [ ] Iterative retrieval skill
- [ ] 55+ tests pass
