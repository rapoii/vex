---
name: secrets-scanning
description: Implement concrete workflows for secrets scanning (git-secrets, truffleHog, regex patterns).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: security
triggers:
  - "scan for secrets"
  - "find leaked keys"
  - "check hardcoded passwords"
  - "secrets-scanning"
---

# Secrets Scanning

Detecting and preventing hardcoded secrets (API keys, passwords, tokens) in source code and repositories.

## When to Activate
- Task involves reviewing code for hardcoded credentials.
- Setting up pre-commit hooks to prevent secret leaks.
- Responding to a suspected secret exposure incident.

## How It Works

### Regular Expression Patterns
Understand the shape of common secrets to build custom scanners or grep commands.

```bash
# AWS Access Key ID
grep -r -E 'AKIA[0-9A-Z]{16}' .

# GCP API Key
grep -r -E 'AIza[0-9A-Za-z\-_]{35}' .

# GitHub Personal Access Token (classic and fine-grained)
grep -r -E 'ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82}' .

# Slack Bot Token
grep -r -E 'xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}' .
```

### Environment Variable Management
Instead of hardcoding, use environment variables and `.env` files.

```python
# Python with python-dotenv
import os
from dotenv import load_dotenv

load_dotenv() # Loads from .env file

API_KEY = os.getenv("EXTERNAL_API_KEY")
if not API_KEY:
    raise ValueError("EXTERNAL_API_KEY is missing")
```

Add `.env` to `.gitignore` immediately:
```bash
echo ".env" >> .gitignore
```

### TruffleHog
TruffleHog scans git repositories, filesystems, and S3 for secrets using regex and entropy checks.

```bash
# Scan a git repository
trufflehog git https://github.com/user/repo.git

# Scan local directory
trufflehog filesystem /path/to/dir
```

### Git-Secrets / Pre-commit Hooks
Prevent secrets from entering git history using `git-secrets` or pre-commit.

```yaml
# .pre-commit-config.yaml using detect-secrets
repos:
-   repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
    -   id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

## Verification Steps
1. Run a scanner over the codebase to ensure no current secrets exist.
2. Verify that `.gitignore` contains all sensitive configuration files (`.env`, `credentials.json`, `*.pem`).
3. If a secret is found in git history, treat it as compromised: Revoke the key immediately at the provider. Removing it from git history using `bfg` or `git filter-repo` is secondary to revocation.

## Common Pitfalls
- **Deleting instead of revoking**: Removing a committed secret from the repo is not enough. Bots scrape public repos in seconds. You MUST revoke the key at the provider.
- **Ignoring test files**: Secrets are often hardcoded in `tests/` or `mocks/`. Use dummy values (`AKIAIOSFODNN7EXAMPLE`) instead.
- **High entropy false positives**: Base64 encoded data, random hashes, and CSS source maps can trigger entropy-based secret scanners. Use baselines to ignore known safe strings.

## Related Skills
- `auth-hardening`: Securely hashing passwords so they don't become leaked secrets.
- `supply-chain-review`: Securing dependencies where malicious actors might exfiltrate secrets.