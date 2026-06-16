# VEX Fix Plan — Pre-Release v1.0.0

**Date:** 2026-06-16
**Source:** Full audit against ECC (ecc.tools, affaan-m/ecc) + Superpowers (obra/superpowers)
**Status:** PLANNING

---

## Problem Summary

VEX has solid infrastructure (192 files, 9 working Python tools, 2,904 lines of real code) tapi:
- **22/41 skills (54%)** = template stubs (54 lines, generic content)
- **32/35 agents (91%)** = identical 34-line templates
- **7/32 features** = missing vs competitors
- **Tests** = 7 failures, 2 errors
- **install.sh profile** = only "default", no minimal/core/full tiers

---

## Fix Plan

### Phase A: Depth — Rewrite Template Content [HIGH PRIORITY]

**A1. Rewrite 22 stub skills (54 lines → 100-300 lines real content)**
- Priority: workflow skills first (most used), then security, then reference
- Each skill needs: real triggers, step-by-step workflow, code examples, verification steps, pitfalls
- Use ECC skills at ~/.claude/skills/ecc/ as reference for depth

Affected skills:
```
skills/automation/ci-cd-setup/SKILL.md
skills/automation/docker-compose/SKILL.md
skills/automation/github-actions/SKILL.md
skills/automation/pre-commit-hooks/SKILL.md
skills/automation/release-automation/SKILL.md
skills/automation/test-automation/SKILL.md
skills/optimization/bundle-optimizer/SKILL.md
skills/optimization/context-window-manager/SKILL.md
skills/optimization/performance-audit/SKILL.md
skills/optimization/query-optimizer/SKILL.md
skills/reference/database-patterns/SKILL.md
skills/reference/fastapi-patterns/SKILL.md
skills/reference/python-patterns/SKILL.md
skills/reference/typescript-patterns/SKILL.md
skills/security/auth-hardening/SKILL.md
skills/security/dependency-audit/SKILL.md
skills/security/secrets-scanning/SKILL.md
skills/security/supply-chain-review/SKILL.md
skills/workflow/deployment-flow/SKILL.md
skills/workflow/feature-development/SKILL.md
skills/workflow/migration-workflow/SKILL.md
skills/workflow/release-workflow/SKILL.md
```

**A2. Rewrite 32 template agents (34 lines → 80-150 lines real content)**
- Each agent needs: unique workflow, domain-specific guidance, output format, escalation rules
- Language agents need: language-specific review checklist, common pitfalls, build commands
- Domain agents need: domain-specific tools, patterns, metrics

Affected agents:
```
agents/core/architect.md, build-error-resolver.md, code-reviewer.md, doc-updater.md,
harness-optimizer.md, loop-operator.md, planner.md, refactor-cleaner.md, security-reviewer.md, tdd-guide.md
agents/domain/accessibility.md, api-designer.md, cloud-architect.md, database.md,
data-engineer.md, devops.md, ml-engineer.md, mobile-dev.md, performance.md, seo.md
agents/language/cpp-reviewer.md, csharp-reviewer.md, dart-reviewer.md, fsharp-reviewer.md,
golang-reviewer.md, java-reviewer.md, kotlin-reviewer.md, php-reviewer.md, python-reviewer.md,
ruby-reviewer.md, rust-reviewer.md, swift-reviewer.md, typescript-reviewer.md
```

### Phase B: Missing Features [MEDIUM PRIORITY]

**B1. Doctor/repair/uninstall CLI**
- Add `vex doctor`, `vex repair`, `vex uninstall` to tools/vex.py
- Doctor: check installation health (files present, tools working, config valid)
- Repair: restore missing files, fix permissions
- Uninstall: backup user data, remove VEX files

**B2. Writing-skills guide (from Superpowers)**
- Create skills/meta/writing-skills/SKILL.md
- How to write good SKILL.md files
- Testing anti-patterns reference
- 100+ lines

**B3. Receiving-code-review (from Superpowers)**
- Create skills/workflow/receiving-code-review/SKILL.md
- How to respond to code review feedback
- When to push back vs accept
- 80+ lines

**B4. Executing-plans skill (from Superpowers)**
- Create skills/workflow/executing-plans/SKILL.md
- Batch execution with human checkpoints
- Progress tracking
- 100+ lines

**B5. Install profiles (minimal/developer/security/full)**
- Update config/profiles.json with real component lists
- Update install.sh to support --profile flag
- minimal: core agents + essential skills
- developer: agents + skills + rules + commands
- security: agents + security skills + hooks
- full: everything

### Phase C: Fix Tests [MEDIUM PRIORITY]

**C1. Fix test_tools.py syntax bug**
- Line 11: `from tools from tools import vex_cost` → fix import

**C2. Fix test failures**
- Install tests: add missing `repair`/`uninstall` commands first (Phase B1)
- Session tests: fix Windows PermissionError (use tempfile properly)

**C3. Target: 80%+ test pass rate**

### Phase D: Cleanup [LOW PRIORITY]

**D1. Remove template boilerplate patterns**
- Search for "Implement concrete workflows and best practices for"
- Replace with real content or remove

**D2. Update CHANGELOG.md**
- Document all fixes

**D3. Final verification**
- All counts match README
- All Python tools compile
- All tests pass
- Dashboard works
- Install works

---

## Execution Order

1. **Phase A1 + A2** (parallel Claude Code workers — biggest task)
2. **Phase B** (parallel workers — new features)
3. **Phase C** (fix tests after features are in)
4. **Phase D** (cleanup + final verification)
5. **Git commit + push**
6. **GitHub release v1.0.0**

---

## Success Criteria

- [ ] 0 template stub skills (all 41 have real content)
- [ ] 0 template agents (all 35 have unique content)
- [ ] All 32 features: ✅ or ⚠️ (no ❌ for critical)
- [ ] Tests: 80%+ pass rate
- [ ] Install profiles working (minimal/developer/security/full)
- [ ] Doctor/repair/uninstall working
- [ ] All counts verified and match README
- [ ] No AI slop, no hallucinated claims
