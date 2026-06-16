---
name: dependency-audit
description: Implement concrete workflows for dependency auditing (npm, pip, cargo, Snyk, Dependabot).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: security
triggers:
  - "audit dependencies"
  - "check vulnerabilities"
  - "update vulnerable packages"
  - "dependency-audit"
---

# Dependency Audit

Workflows and best practices for auditing dependencies, identifying vulnerabilities, and keeping third-party packages secure.

## When to Activate
- Task involves updating dependencies to fix CVEs.
- Setting up CI/CD pipeline security checks.
- Reviewing package.json, requirements.txt, or Cargo.toml for known vulnerable versions.

## How It Works

### Node.js / npm
Use `npm audit` to check for known vulnerabilities.

```bash
# Run a dry audit
npm audit

# Fix non-breaking vulnerabilities automatically
npm audit fix

# Force fix (WARNING: can break dependencies by jumping major versions)
npm audit fix --force
```

In CI, you often want to fail the build on high/critical vulnerabilities:
```bash
npm audit --audit-level=high
```

### Python / pip
Use `pip-audit` or `safety` to scan Python environments and requirements files.

```bash
# Install pip-audit
pip install pip-audit

# Audit a requirements file
pip-audit -r requirements.txt

# Audit the current environment
pip-audit
```

### Rust / Cargo
Use `cargo-audit` to check dependencies against the RustSec Advisory Database.

```bash
# Install cargo-audit
cargo install cargo-audit

# Run audit
cargo audit
```

### Automated Tools (Dependabot / Snyk)
Enable automated scanning in GitHub via Dependabot.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
```

## Verification Steps
1. Run the local audit command for the respective language to identify current issues.
2. Review the vulnerability database entry (e.g., GitHub Advisory or CVE) to understand the impact.
3. Update the package version in the manifest and regenerate the lockfile.
4. Run tests to ensure the updated dependency does not break existing functionality.

## Common Pitfalls
- **Ignoring lockfiles**: Always commit `package-lock.json`, `poetry.lock`, or `Cargo.lock`. Audits rely on these to know exact installed versions.
- **Blindly applying `--force`**: `npm audit fix --force` can upgrade major versions, breaking your application. Test thoroughly.
- **Ignoring transitive dependencies**: A vulnerability deep in the dependency tree requires updating the top-level package that brings it in, or using dependency overrides/resolutions.

## Related Skills
- `supply-chain-review`: For deeper software supply chain integrity checks.
- `secrets-scanning`: To ensure secrets aren't leaked in package manifests or code.