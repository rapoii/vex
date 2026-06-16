# VEX Fix Plan v4 — HIGH Priority Gaps

**Date:** 2026-06-16
**Source:** Gap analysis v ECC + Superpowers
**Method:** Claude Code + ECC active, kanban orkestra multi-agent swarm
**Status:** EXECUTING

---

## 6 HIGH Priority Gaps

### 1. AgentShield — Standalone Security Auditor [CRITICAL]

**ECC reference:** `npx ecc-agentshield scan` — 1282 tests, 102 rules, secrets/permissions/hooks/MCP/agent config scanning

**VEX plan:**
- Create `tools/vex_shield.py` — standalone security auditor CLI
- 102 security rules (reuse from vex_security.py, expand)
- Scan modes: `vex shield scan [--target agents|hooks|skills|tools|all]`
- Categories: secrets, permissions, hooks, agent config, dependency, supply-chain
- Output: JSON report with CRITICAL/HIGH/MEDIUM/LOW findings
- `vex shield report` — generate markdown report
- `vex shield ci` — CI mode (exit 1 if CRITICAL found)
- Only Python stdlib

### 2. Skill Creator from Git History [CRITICAL]

**ECC reference:** `/skill-create` — analyzes git history → generates SKILL.md

**VEX plan:**
- Create `tools/vex_skill_create.py` — git history → SKILL.md generator
- Analyze recent commits (last N days/files)
- Extract common patterns: files frequently changed together, recurring commands, fix patterns
- Generate SKILL.md with: triggers, workflow, code examples
- CLI: `python tools/vex_skill_create.py [--days 30] [--output skills/]`
- Only Python stdlib + git subprocess

### 3. Instinct Import/Evolve [CRITICAL]

**ECC reference:** `/instinct-import`, `/instinct-export`, `/evolve` — share and cluster instincts

**VEX plan:**
- Enhance `tools/vex_instinct.py` with:
  - `vex instinct export [--output instincts.json]` — export instincts to shareable JSON
  - `vex instinct import <file>` — import instincts from JSON
  - `vex instinct evolve` — cluster related instincts into skill candidates
  - `vex instinct prune [--threshold 0.3]` — remove low-confidence instincts
- Update vex.py CLI with new subcommands

### 4. GateGuard — Destructive Command Blocker [CRITICAL]

**ECC reference:** Gates destructive shell commands before execution

**VEX plan:**
- Create `hooks/scripts/gate-guard.py` — block dangerous commands
- Patterns to block: `rm -rf /`, `git push --force` to main, `DROP TABLE`, `kubectl delete`
- Patterns to warn: `sudo`, `chmod 777`, `curl | bash`
- Config: `hooks/gate-guard-rules.json` — customizable patterns
- CLI: `vex guard status` — show blocked commands
- Hook integration: fires on PreToolUse for Bash tool

### 5. Eval Harness — Verification Loops [CRITICAL]

**ECC reference:** Verification loop evaluation with grader types, pass@k metrics

**VEX plan:**
- Create `tools/vex_eval.py` — evaluation harness
- Run agent task multiple times, measure pass@k
- Grader types: exact_match, contains, regex, llm_judge
- CLI: `python tools/vex_eval.py run --task "fix bug" --iterations 5 --grader contains`
- Output: pass@k score, average time, cost estimate
- Only Python stdlib

### 6. AgentShield --opus (Red/Blue Team) [CRITICAL]

**ECC reference:** 3 Claude Opus agents in adversarial pipeline

**VEX plan:**
- Create `tools/vex_redteam.py` — adversarial security analysis
- Pipeline: Red Agent (find vulnerabilities) → Blue Agent (propose fixes) → Auditor Agent (verify)
- CLI: `python tools/vex_redteam.py --target <dir> [--depth quick|deep]`
- Output: adversarial report with attack vectors + defenses
- Uses Claude Code proxy for agent calls
- Only Python stdlib + subprocess (claude -p)

---

## Execution

3 Claude Code workers (kanban swarm):

| Worker | Tasks | Status |
|--------|-------|--------|
| **Security** | AgentShield (vex_shield.py) + GateGuard (gate-guard.py) | 🔄 |
| **Intelligence** | Skill Creator (vex_skill_create.py) + Instinct Evolve (vex_instinct.py) | 🔄 |
| **Verification** | Eval Harness (vex_eval.py) + Red/Blue Team (vex_redteam.py) | 🔄 |

After all workers:
- Verify all 6 tools compile + have CLI
- Run tests (target: 50+ tests pass)
- Update vex.py with new subcommands
- Update AGENTS.md, README.md
- Commit + push

---

## Success Criteria

- [ ] vex_shield.py — standalone auditor, 102 rules, scan/report/ci modes
- [ ] vex_skill_create.py — git history → SKILL.md generator
- [ ] vex_instinct.py — export/import/evolve/prune commands
- [ ] gate-guard.py — blocks destructive commands, customizable rules
- [ ] vex_eval.py — eval harness with pass@k metrics
- [ ] vex_redteam.py — red/blue team adversarial pipeline
- [ ] All tools compile + have argparse CLI
- [ ] 50+ tests pass
- [ ] vex.py updated with new subcommands
- [ ] Committed + pushed
