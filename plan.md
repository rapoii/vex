# VEX Fix Plan v3 — Remaining Weaknesses

**Date:** 2026-06-16
**Source:** Honest self-audit after v1.0.0 release
**Status:** PLANNING

---

## Weak Points to Fix

### 1. Hook System — Scripts Minimal [HIGH]

**Current:** hooks.json has event types (PostToolUse, PreToolUse, Stop, SessionStart, SessionEnd) but hook scripts are stubs or minimal.

**Fix:**
- hooks/scripts/check-file-size.py — implement actual file size check (block >1MB writes)
- hooks/scripts/validate-frontmatter.py — implement YAML frontmatter validation for SKILL.md/agent files
- hooks/scripts/post-tool-use.py — NEW: log tool usage, track costs per tool call
- hooks/scripts/stop.py — NEW: generate session summary on stop
- Update hooks.json to reference all scripts properly

### 2. Dashboard Search — Not Implemented [HIGH]

**Current:** Dashboard has routes for /, /agents, /skills, /costs, /memory, /health but NO /search endpoint.

**Fix:**
- Add GET /search?q=<query> to dashboard/server.py
- Search across agents, skills, commands, rules by name and description
- Add search box to base.html template header
- HTMX-powered: type to search, results update live
- Filter by type (agent/skill/command/rule)

### 3. Pipeline Cross-References — Only 1 Skill Has Them [MEDIUM]

**Current:** Only executing-plans has "Next:" links. Other workflow skills are disconnected.

**Fix:** Add "Next Step" and "Previous Step" links to ALL workflow skills:
- brainstorming → worktree-isolation
- worktree-isolation → executing-plans OR subagent-development
- executing-plans → strict-tdd OR tdd-workflow
- strict-tdd → code-review-flow
- code-review-flow → receiving-code-review
- receiving-code-review → verification-before-completion
- verification-before-completion → finishing-development-branch
- bug-fix-flow → verification-before-completion
- feature-development → code-review-flow
- deployment-flow → verification-before-completion
- release-workflow → deployment-flow
- subagent-development → code-review-flow
- dispatching-parallel-agents → subagent-development

### 4. vex doctor — Checks Wrong Path [MEDIUM]

**Current:** doctor checks ~/.claude/ (install path) but should also check project-local state.

**Fix:**
- Add project-local checks: VEX project files present (agents/, skills/, tools/)
- Add hook system check: hooks.json valid, all referenced scripts exist
- Add adapter check: all adapter JSON files valid
- Add marketplace check: catalog.json valid
- Add dashboard check: server.py syntax OK
- Add disk usage report
- Fix: doctor should work both in installed mode AND project mode

### 5. Dashboard Auth — Not Verified End-to-End [LOW]

**Current:** Token auth exists in server.py but not tested.

**Fix:**
- Verify token generation works
- Verify unauthorized requests are blocked
- Add test for auth flow
- Document auth usage in dashboard/README.md

### 6. Hook Runtime Env Vars — Structure Only [LOW]

**Current:** VEX_HOOK_PROFILE and VEX_DISABLED_HOOKS referenced in hooks.json but vex_hooks.py may not fully implement.

**Fix:**
- Verify vex_hooks.py reads env vars
- Verify profile switching works
- Verify disable mechanism works
- Add tests

---

## Execution Order

1. **Hook scripts** (1) — implement real logic
2. **Dashboard search** (2) — add /search endpoint + UI
3. **Pipeline cross-refs** (3) — add links to all workflow skills
4. **Doctor enhancement** (4) — fix path checks
5. **Auth verification** (5) — test + document
6. **Hook runtime verification** (6) — test env vars
7. **Final test run** — 42/42 pass target
8. **Commit + push**

---

## Success Criteria

- [ ] All 4+ hook scripts have real implementation (not stubs)
- [ ] Dashboard /search works (type to search agents/skills)
- [ ] All 14 workflow skills have pipeline cross-references
- [ ] vex doctor checks 12+ items (project + install)
- [ ] Dashboard auth verified
- [ ] Hook env vars verified
- [ ] 42/42 tests pass
- [ ] All changes committed + pushed
