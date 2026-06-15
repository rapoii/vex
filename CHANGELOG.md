# Changelog

All notable changes to VEX will be documented in this file.

## [1.0.0] - 2026-06-16

### Added
- Core agent orchestration system (Planner, Code Reviewer, Security Reviewer, TDD Guide).
- Rule engine with common and language-specific guidance (TypeScript, Python, Go, Rust, Web).
- CLI tools for skill generation (`vex-skill-gen.py`), cost reporting (`vex-cost.py`), and memory management (`vex-memory.py`).
- PreToolUse and PostToolUse hook system for Claude Code.
- VEX Marketplace with `catalog.json` and installer CLI for community skill distribution.
- Comprehensive test suite covering tools, hooks, and installer mechanics.

### Security
- Integrated file-size check hook to prevent token exhaustion.
- Path traversal protection in the marketplace installer.
