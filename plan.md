# VEX Fix Plan v6 — LOW Priority Gaps

**Date:** 2026-06-16
**Source:** Gap analysis v ECC + Superpowers
**Status:** EXECUTING

---

## LOW Priority Gaps (Doable)

### 1. Systematic Debugging Skill [from Superpowers]
- Create skills/workflow/systematic-debugging/SKILL.md
- 4-phase root cause: reproduce → isolate → identify → fix
- Defense-in-depth: fix root cause + add guardrails
- 120+ lines

### 2. Harness Audit Scoring
- Create tools/vex_audit.py — deterministic harness audit
- Score: reliability, risk, coverage, security
- CLI: python tools/vex_audit.py [--harness claude-code] [--json]
- Check: hooks working, agents valid, skills complete, rules enforced
- Output: score 0-100 per category + overall

### 3. llms.txt — LLM Documentation
- Create llms.txt at project root
- Comprehensive LLM docs: what VEX is, how to use it, file structure, conventions
- Machine-readable for LLMs consuming the repo

### 4. Business/Content Skills
- Create skills/reference/article-writing/SKILL.md — technical writing patterns
- Create skills/reference/content-engine/SKILL.md — content generation workflow

### 5. Media/Video Skills  
- Create skills/reference/video-production/SKILL.md — video creation with Manim, Remotion

### 6. Factory Droid Adapter
- Create adapters/factory-droid.json — Factory Droid harness adapter
- File mapping, feature support matrix

### 7. Onboarding Skill [from Superpowers]
- Create skills/meta/using-vex/SKILL.md — introduction to VEX system
- How to install, configure, use agents/skills/hooks
- 100+ lines

### 8. NanoClaw-lite (Model Routing)
- Create tools/vex_route.py — intelligent model routing
- Route by task type: architecture→opus, coding→sonnet, exploration→haiku
- CLI: python tools/vex_route.py --task "fix bug" --budget 0.50
- Cost-aware routing

---

## Execution

2 Claude Code workers:

| Worker | Tasks |
|--------|-------|
| **Skills+Meta** | systematic-debugging, article-writing, content-engine, video-production, using-vex |
| **Tools+Config** | vex_audit.py, vex_route.py, llms.txt, factory-droid adapter |

---

## Success Criteria

- [ ] systematic-debugging skill (120+ lines)
- [ ] 3 new reference/meta skills
- [ ] vex_audit.py — harness scoring
- [ ] vex_route.py — model routing
- [ ] llms.txt — machine-readable docs
- [ ] factory-droid adapter
- [ ] using-vex onboarding skill
- [ ] 55+ tests pass
