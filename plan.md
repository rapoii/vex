# VEX Fix Plan v2 — Full Audit Results

**Date:** 2026-06-16
**Sources:** ecc.tools, github.com/affaan-m/ecc, github.com/obra/superpowers
**Method:** All data from actual command output or browser extraction. No hallucination.

---

## Current VEX State (Verified)

| Component | Count | Lines | Status |
|-----------|-------|-------|--------|
| Files | 200 | — | ✅ |
| Agents | 35 (12 core, 10 domain, 13 language) | 71-139 each | ✅ Real content |
| Skills | 44 (6 auto, 1 meta, 8 opt, 8 ref, 7 sec, 14 wf) | 87-522 each | ✅ Real content |
| Rules | 27 (11 frameworks) | — | ✅ |
| Tools | 12 Python modules | 4,757 total | ✅ All compile |
| Tests | 45 | — | ✅ 100% pass |
| Commands | 10 | — | ✅ |
| Contexts | 5 | — | ✅ |
| Hooks | 6 files (4 scripts) | — | ⚠️ session-start/summary are 1-line stubs |
| Adapters | 7 harnesses | — | ✅ JSON valid |
| Dashboard | Flask web app | 396 lines | ✅ Working |
| Marketplace | catalog + installer | — | ✅ Clean data |
| Install profiles | 5 profiles | — | ✅ |

---

## Competitor State (Verified from live repos)

### ECC (github.com/affaan-m/ecc)

| Feature | ECC Count |
|---------|-----------|
| Skills | 271 |
| Agents | 67 |
| Commands | 92 legacy shims |
| Harnesses | 11+ (Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Zed, Copilot, Antigravity, JoyCode, Qwen, Grok) |
| Hook events | 8 (Claude Code), 15 (Cursor), 11 (OpenCode) |
| Install profiles | minimal, core, full |
| Dashboard | Tkinter desktop (dark/light, font, tabs, search) |
| i18n | 12 languages |
| Hook runtime | ECC_HOOK_PROFILE, ECC_DISABLED_HOOKS, ECC_SESSION_START_MAX_CHARS |
| Session store | SQLite |
| Continuous learning | Instinct system with confidence scoring |
| AgentShield | 102 rules, standalone scanner |
| Doctor/repair | ✅ |

### Superpowers (github.com/obra/superpowers)

| Feature | Superpowers Count |
|---------|-------------------|
| Skills | 14 |
| Harnesses | 8 (Claude Code, Codex CLI/App, Factory Droid, Gemini CLI, OpenCode, Cursor, Copilot CLI) |
| TDD | Strict RED-GREEN-REFACTOR, deletes pre-test code |
| Subagent dev | Fresh subagent per task, two-stage review |
| Worktree isolation | Auto worktree + branch per task |
| Brainstorming | Socratic design refinement |
| Pipeline | brainstorm → worktree → plans → execute → TDD → review → finish |

---

## Gap Analysis (Verified)

### ✅ VEX Has (competitors don't)

| Feature | VEX | ECC | Superpowers |
|---------|-----|-----|-------------|
| Auto-skill generation tool | ✅ | ❌ | ❌ |
| Cross-project memory (knowledge graph) | ✅ | ❌ | ❌ |
| Cost intelligence (budgets, tracking, charts) | ✅ | Pro only | ❌ |
| Unified adapter layer (7 harnesses, 1 installer) | ✅ | Per-harness | Per-harness |
| Skill testing framework | ✅ | ❌ | ❌ |
| Decentralized marketplace (GitHub Releases) | ✅ | GitHub App | ❌ |
| Token optimization (4 skills + tool) | ✅ | Partial | ❌ |

### ❌ VEX Missing vs ECC

| Gap | ECC | VEX | Priority |
|-----|-----|-----|----------|
| Skill count | 271 | 44 | 🟡 Scale — VEX has quality, ECC has quantity |
| Agent count | 67 | 35 | 🟡 Missing: e2e-runner, docs-lookup, chief-of-staff, mle-reviewer, database-reviewer, etc. |
| Command count | 92 | 10 | 🟡 Legacy shims — not critical |
| Harness count | 11+ | 7 | 🟡 Missing: Antigravity, JoyCode, Qwen, Grok |
| i18n (12 languages) | ✅ | ❌ | 🟡 Nice-to-have |
| Hook event types | 8-15 per harness | 4 basic | 🔴 Hook system shallow |
| Dashboard features | Tkinter (tabs, search, font, themes) | Flask (basic routes) | 🟡 Different approach, missing search/filter |
| AgentShield (standalone scanner) | ✅ | ❌ | 🟡 vex_security.py exists but not standalone package |
| Hook runtime env vars | ECC_HOOK_PROFILE + 3 more | profiles.json only | 🟡 Missing env var controls |
| Session store | SQLite | ❌ | 🟡 vex_sessions.py exists but not integrated |
| Continuous learning | Instinct system (confidence scoring, import/export/evolve/prune) | vex_instinct.py (basic) | 🟡 Missing import/export/evolve/prune commands |

### ❌ VEX Missing vs Superpowers

| Gap | Superpowers | VEX | Priority |
|-----|-------------|-----|----------|
| Strict TDD enforcement (deletes pre-test code) | ✅ | ⚠️ skill exists, not enforced | 🔴 Core differentiator |
| Full pipeline integration | 7-step pipeline connected | Skills exist but disconnected | 🔴 Workflow gap |
| Factory Droid harness | ✅ | ❌ | 🟢 Niche |
| Verification-before-completion skill | ✅ | ❌ | 🟡 Implicit in TDD |

### ⚠️ VEX Has But Weak

| Component | Issue | Fix |
|-----------|-------|-----|
| hooks/scripts/session-start.py | 1-line stub | Implement actual session tracking |
| hooks/scripts/session-summary.py | 1-line stub | Implement actual summary generation |
| hooks event types | Only 4 (PreToolUse, PostToolUse, Stop, SessionStart) | Add more event types |
| 3 broken-path directories | `C:Usersrafivex-project*` phantom dirs | Delete |
| install.sh | Unstaged changes | Commit |

---

## Fix Plan

### Phase 1: Cleanup (Quick Wins)

1. **Delete 3 phantom directories** at repo root (`C:Usersrafivex-project*`)
2. **Commit install.sh changes**
3. **Implement session-start.py** — actual session tracking (record start time, project, model)
4. **Implement session-summary.py** — actual summary generation (duration, files changed, cost)

### Phase 2: Missing Skills (from Superpowers pipeline)

5. **Create skills/workflow/verification-before-completion/SKILL.md** — verify fix actually works before declaring success
6. **Create skills/workflow/finishing-development-branch/SKILL.md** — merge/PR/keep/discard decisions after worktree work
7. **Create skills/workflow/requesting-code-review/SKILL.md** — how to request and structure code reviews
8. **Create skills/workflow/dispatching-parallel-agents/SKILL.md** — concurrent subagent coordination

### Phase 3: Missing Agents

9. **Create agents/core/e2e-runner.md** — end-to-end test specialist
10. **Create agents/core/docs-lookup.md** — documentation search specialist
11. **Create agents/domain/database-reviewer.md** — database code review
12. **Create agents/domain/mle-reviewer.md** — ML engineering review

### Phase 4: Hook System Enhancement

13. **Enhance hooks.json** — add more event types (PostToolUse, SessionEnd)
14. **Add env var controls** — VEX_HOOK_PROFILE, VEX_DISABLED_HOOKS to vex_hooks.py
15. **Implement hook runtime** — actually fire hooks on events

### Phase 5: Integration

16. **Connect skills into pipeline** — brainstorming → worktree → plans → execute → TDD → review → finish
17. **Add search/filter to dashboard** — text search across agents/skills
18. **Enhance vex doctor** — check hook system, adapters, marketplace

### Phase 6: Verification

19. **Run all tests** — target 100% pass
20. **Verify all counts match README**
21. **Commit + push + GitHub release v1.0.0**

---

## Success Criteria

- [ ] 0 phantom directories
- [ ] 0 stub scripts (session-start, session-summary implemented)
- [ ] 4 new skills (verification, finishing-branch, requesting-review, dispatching-parallel)
- [ ] 4 new agents (e2e-runner, docs-lookup, database-reviewer, mle-reviewer)
- [ ] Hook system enhanced (more events, env vars)
- [ ] Pipeline connected (skills reference each other)
- [ ] Dashboard has search/filter
- [ ] All tests pass
- [ ] All counts verified
