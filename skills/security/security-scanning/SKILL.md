---
name: security-scanning
description: Run security scans, interpret severity levels, and remediate vulnerabilities systematically.
category: security
whenToUse: Before merging critical features, before releases, or when requested to perform a security audit on the codebase.
---

# Security Scanning

Automated security scanning prevents known vulnerabilities from reaching production. This workflow defines how to execute scans, triage results, and apply fixes systematically.

## Triggers

Activate this workflow when:
- Preparing for a release or deploying to production.
- Implementing auth, payment, or data-handling features.
- The user requests a "security scan" or "vulnerability check".
- CI/CD pipelines report a security failure.

## Executing the Scan

Run the VEX security scanner locally to identify issues before committing.

### Running `vex_security.py`

The primary tool is `vex_security.py`.

```bash
# Basic scan of the current directory
python scripts/vex_security.py scan .

# Scan specific directory with detailed output
python scripts/vex_security.py scan src/ --verbose

# Output results as JSON for CI integration
python scripts/vex_security.py scan . --format json --output results.json
```

## Interpreting Severity Levels

The scanner categorizes findings into four levels. Handle them according to this matrix:

| Level | Definition | Action Required |
|-------|------------|-----------------|
| **CRITICAL** | Exploitable vulnerability causing immediate data loss, RCE, or full system compromise. (e.g., Hardcoded AWS keys, SQLi in public endpoint). | **BLOCK.** Drop all other tasks. Fix immediately. Do not merge. |
| **HIGH** | Significant risk, high impact but may require specific conditions to exploit. (e.g., Missing CSRF, vulnerable dependency with known exploit). | **BLOCK.** Must fix before merging to mainline branches. |
| **MEDIUM** | Moderate risk, often defense-in-depth failures or configuration issues. (e.g., Missing security headers, permissive CORS). | **FIX SOON.** Create a ticket. Should not block emergency hotfixes. |
| **LOW** | Minor issues, informational findings, or theoretical risks. (e.g., Information disclosure in stack traces). | **LOG.** Address when modifying related code. |

## Triaging and Remediation

When scan results are generated, follow this process:

### 1. Validate Findings (Avoid False Positives)
Review each finding to ensure it's actionable.
- Does the code actually execute in a sensitive context?
- Is the "secret" actually a test credential or a public identifier?
- *Action:* If a false positive is confirmed, use the suppression mechanism (e.g., inline comments like `# vex-sec: ignore` or updating the suppression file) and document *why* it's safe.

### 2. Remediate Systematic Issues
Fix root causes, not just symptoms.

#### Example: Hardcoded Secrets
*Finding:* CRITICAL - Hardcoded API Key
*Fix:* Remove the key from code, revoke it immediately, and replace with environment variables.
```python
# BAD
api_key = "sk_live_123456789"
stripe.api_key = api_key

# GOOD
import os
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise ValueError("STRIPE_SECRET_KEY must be set")
```

#### Example: SQL Injection
*Finding:* HIGH - Unsafe query construction
*Fix:* Always use parameterized queries or ORM methods.
```python
# BAD
cursor.execute(f"SELECT * FROM users WHERE username = '{user_input}'")

# GOOD
cursor.execute("SELECT * FROM users WHERE username = %s", (user_input,))
```

#### Example: Path Traversal
*Finding:* HIGH - Unsanitized file path
*Fix:* Validate paths and ensure they resolve within expected directories.
```python
# BAD
with open(f"/var/www/uploads/{user_filename}", "r") as f:
    return f.read()

# GOOD
import os
from werkzeug.utils import secure_filename

safe_name = secure_filename(user_filename)
upload_dir = "/var/www/uploads/"
full_path = os.path.abspath(os.path.join(upload_dir, safe_name))

if not full_path.startswith(upload_dir):
    raise SecurityException("Invalid path")
```

### 3. Verify Fixes
Re-run the scanner to confirm the specific findings are resolved.
```bash
python scripts/vex_security.py scan path/to/fixed/file.py
```

## CI/CD Integration

Security scans must be integrated into automated pipelines to prevent regressions.

### GitHub Actions Example
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run VEX Security Scanner
        run: |
          python scripts/vex_security.py scan . --fail-on HIGH,CRITICAL
```

*Note:* The pipeline should fail (exit code > 0) only on HIGH and CRITICAL findings. MEDIUM and LOW should output warnings.

## Agent Handoff

For complex vulnerabilities requiring architectural changes, hand off triage and remediation planning to the specialized agent:

1. Save the scan output.
2. Launch the `security-reviewer` agent with the scan results.
3. Ask the agent to provide an implementation plan for the fixes.

## Related Skills
- `auth-hardening`
- `dependency-audit`
