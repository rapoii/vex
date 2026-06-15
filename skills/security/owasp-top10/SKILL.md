---
name: owasp-top10
description: Check app code against OWASP Top 10 with concrete mitigation patterns.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: security
  triggers: ["Security review", "User input/API/auth changes", "Pre-release audit"]
---

# OWASP Top 10 Mitigation

Concrete patterns for identifying and mitigating the most critical web application security risks.

## When to Activate

- Auditing security-sensitive code.
- Reviewing authentication or authorization changes.
- Handling user input, file uploads, or database queries.

## Top 10 Categories & Mitigations

### 1. Broken Access Control
Users acting outside their intended permissions.
- **Pattern**: Deny by default.
- **Check**: Are API endpoints checking if the user *owns* the resource, not just if they are logged in?
- **Fix**: Use role-based (RBAC) or attribute-based (ABAC) access control consistently.

### 2. Cryptographic Failures
Exposure of sensitive data (passwords, PII).
- **Pattern**: Hash passwords with strong algorithms (Argon2, bcrypt).
- **Check**: Are secrets hardcoded? Is HTTP used instead of HTTPS?
- **Fix**: Encrypt data at rest and in transit. Never roll your own crypto.

### 3. Injection (SQL, NoSQL, Command)
Untrusted data sent to an interpreter.
- **Pattern**: Parameterized queries.
- **Check**: Is string concatenation used in SQL queries or `exec()` calls?
- **Fix**:
  ```python
  # ❌ Bad
  db.execute(f"SELECT * FROM users WHERE name = '{user_input}'")
  # ✅ Good
  db.execute("SELECT * FROM users WHERE name = ?", (user_input,))
  ```

### 4. Insecure Design
Flaws in architecture.
- **Pattern**: Threat modeling during design.
- **Check**: Are business logic limits enforced? (e.g., maximum order quantity).
- **Fix**: Implement secure defaults.

### 5. Security Misconfiguration
Insecure default settings, open cloud storage.
- **Pattern**: Hardened environments.
- **Check**: Are debug modes enabled in production? Are S3 buckets public?
- **Fix**: Disable debug features in prod. Use automated configuration auditing.

### 6. Vulnerable and Outdated Components
Using libraries with known CVEs.
- **Pattern**: Dependency management.
- **Check**: Are `npm audit` or `dependabot` checks failing?
- **Fix**: Regularly update dependencies. Remove unused packages.

### 7. Identification and Authentication Failures
Session management issues, credential stuffing.
- **Pattern**: Secure sessions.
- **Check**: Are session IDs exposed in URLs? Are passwords weak?
- **Fix**: Enforce MFA. Use secure, HttpOnly cookies for sessions.

### 8. Software and Data Integrity Failures
CI/CD pipeline compromises, unverified updates.
- **Pattern**: Verify origins.
- **Check**: Are you downloading dependencies over unencrypted connections?
- **Fix**: Use package lock files (`package-lock.json`). Sign commits.

### 9. Security Logging and Monitoring Failures
Inability to detect active breaches.
- **Pattern**: Audit trails.
- **Check**: Do you log failed login attempts?
- **Fix**: Log all security events. Ensure logs don't contain sensitive data (passwords).

### 10. Server-Side Request Forgery (SSRF)
Server fetches a user-provided URL without validation.
- **Pattern**: Allow-lists for outbound requests.
- **Check**: Does the app download an image from a user-supplied URL?
- **Fix**: Validate the URL against an allow-list. Block requests to internal IP addresses (e.g., `127.0.0.1`, `169.254.169.254`).

## Review Workflow

1. Identify boundaries where untrusted data enters the system.
2. Verify validation and sanitization at those boundaries.
3. Check authentication/authorization at the resource level.
4. Ensure safe data storage (encryption/hashing).
