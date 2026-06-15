# VEX — Vareva ECC Extended

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Cost](https://img.shields.io/badge/cost-100%25%20free-brightgreen.svg)](SOUL.md)
[![Harness](https://img.shields.io/badge/harness-Claude%20Code%20first-purple.svg)](CLAUDE.md)
[![Status](https://img.shields.io/badge/status-foundation-orange.svg)](#roadmap)

VEX is a free, MIT-licensed agent harness system for building, testing, routing, and evolving AI coding workflows. It starts with Claude Code because that is where the highest-leverage agent ergonomics exist today, then expands through a cross-harness adapter layer.

## Features

- **Claude Code first**: agents, skills, commands, rules, hooks, and contexts optimized for Claude Code.
- **Auto-skill generation**: mine repeated workflows and convert them into tested reusable skills.
- **Cost intelligence**: estimate, track, and compare model/tool spend before and after runs.
- **Cross-project memory**: portable user, feedback, project, and reference memories with scoped access.
- **Skill testing**: fixture-driven checks for skill triggers, instructions, and expected outputs.
- **Web dashboard**: local dashboard for packs, runs, costs, skills, hooks, and health checks.
- **Skill Marketplace**: browse, install, and rate community-curated skills via GitHub releases.
- **Cross-harness adapters**: one manifest, many targets; Claude Code first, other harnesses later.

## Install

```bash
git clone https://github.com/rapoii/vex.git
cd vex
npm install
python -m pip install -e .
```

Claude Code bootstrap target:

```bash
npm run vex -- install --target claude-code --profile default
```

## Marketplace

VEX includes a free, decentralized skill marketplace powered by GitHub Releases.

```bash
# Browse available skills
python marketplace/installer.py browse

# Install a skill
python marketplace/installer.py install <skill-name>
```

## Testing & Contributing

VEX uses standard Python `unittest` for its core tooling to stay lightweight.

```bash
python -m unittest discover -s tests
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to publish your own skills to the marketplace.

## Project structure

```text
agents/      Agent definitions and orchestration roles
skills/      Reusable task workflows and domain playbooks
commands/    Slash-command wrappers and command metadata
rules/       Always-on coding, security, testing, and harness rules
hooks/       PreToolUse, PostToolUse, Stop, and notification hooks
contexts/    Project, harness, model, and environment context templates
config/      Pack manifests, adapter config, defaults, and schemas
tools/       Shared TypeScript/Python implementation modules
scripts/     Validation, packaging, migration, and release scripts
marketplace/ Marketplace catalog and installer CLI
tests/       Core system unit tests
```

## ECC vs VEX

| Area | ECC baseline | VEX foundation |
| --- | --- | --- |
| License | Project-dependent distribution | MIT, 100% free forever |
| Harness focus | Claude Code rules, agents, skills | Claude Code first plus adapter layer |
| Skills | Hand-authored skills | Hand-authored plus auto-skill generation |
| Cost visibility | Manual or external tracking | Built-in cost intelligence and reports |
| Memory | Claude memory conventions | Cross-project memory packs with scopes |
| Quality | Human review and tests | Skill tests, lint checks, dashboard health |
| UI | CLI/file-first | CLI/file-first with web dashboard roadmap |

## Roadmap

1. **Phase 1: Foundation** — docs, manifests, validation, architecture, package metadata.
2. **Phase 2: Claude Code pack** — installable agents, skills, rules, commands, hooks.
3. **Phase 3: Intelligence** — auto-skill generation, cost reports, memory indexing.
4. **Phase 4: Dashboard** — local web app for runs, skills, costs, and health.
5. **Phase 5: Cross-harness** — adapters for other agent harnesses.

## Philosophy

VEX stays free forever. No paid core, no locked agents, no premium rules, no telemetry requirement. See [SOUL.md](SOUL.md).

## License

MIT © 2026 Rafi Permana.
