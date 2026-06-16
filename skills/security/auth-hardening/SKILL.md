---
name: auth-hardening
description: Implement concrete workflows and best practices for authentication hardening (JWT, session, OAuth2, MFA, password hashing).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: security
triggers:
  - "harden auth"
  - "improve authentication"
  - "secure login"
  - "auth-hardening"
---

# Authentication Hardening

Best practices for securing authentication mechanisms, managing sessions, handling tokens, and storing credentials securely.

## When to Activate
- Task involves creating or reviewing login, registration, or password reset flows.
- Reviewing session management or JWT usage.
- Implementing OAuth2 or MFA (Multi-Factor Authentication).
- Storing passwords or sensitive user credentials.

## How It Works

### Password Hashing (Argon2 / bcrypt)
Never store passwords in plain text. Use Argon2 (preferred) or bcrypt.

```python
# Python with passlib and argon2-cffi
from passlib.hash import argon2

def hash_password(plain_password: str) -> str:
    return argon2.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2.verify(plain_password, hashed_password)
```

```typescript
// Node.js with bcrypt
import bcrypt from 'bcrypt';

const saltRounds = 12;

export async function hashPassword(plainText: string): Promise<string> {
  return await bcrypt.hash(plainText, saltRounds);
}

export async function verifyPassword(plainText: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(plainText, hash);
}
```

### JWT Best Practices
JWTs should have short expiration times, use strong signing algorithms (e.g., RS256 or HS256 with a strong secret), and include the `exp` and `iat` claims.

```typescript
// Node.js JWT issuing
import jwt from 'jsonwebtoken';

export function generateToken(userId: string): string {
  // Use a strong, long, random secret key from env
  const secret = process.env.JWT_SECRET!;
  return jwt.sign(
    { sub: userId, type: 'access' },
    secret,
    { expiresIn: '15m', algorithm: 'HS256' } // Short expiration!
  );
}
```

### Session Management
If using stateful sessions, ensure cookies are `HttpOnly`, `Secure`, `SameSite=Strict`.

```typescript
// Express session configuration
import session from 'express-session';

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // true over HTTPS
    httpOnly: true, // Prevent XSS access
    sameSite: 'strict', // Prevent CSRF
    maxAge: 1000 * 60 * 60 * 24 // 1 day
  }
}));
```

### Multi-Factor Authentication (MFA)
Require MFA for sensitive operations. Use TOTP (Time-based One-Time Password) standards.

```python
# Python pyotp example
import pyotp

# Generate a secret for the user
user_secret = pyotp.random_base32()
# Generate provisioning URI for Google Authenticator
uri = pyotp.totp.TOTP(user_secret).provisioning_uri(name="user@domain.com", issuer_name="My App")

# Verify
totp = pyotp.TOTP(user_secret)
is_valid = totp.verify("123456")
```

## Verification Steps
1. Verify password hashes in DB to ensure plain texts aren't stored.
2. Inspect cookies in the browser network tab to ensure `Secure` and `HttpOnly` flags are present.
3. Decode JWTs using jwt.io (never input real production tokens) to check that `exp` is reasonably short (e.g., 15-60 minutes).
4. Run static analysis tools (e.g., Bandit for Python, ESLint security plugins for JS) to catch hardcoded secrets or weak hashing usage.

## Common Pitfalls
- **Using MD5 or SHA-1 for passwords**: These are completely broken. Use Argon2 or bcrypt.
- **Long-lived access tokens**: Access tokens should live minutes, not days. Use refresh tokens for long-lived sessions.
- **Storing JWTs in localStorage**: This exposes them to XSS attacks. Store them in `HttpOnly` cookies if interacting with a first-party API.
- **Missing CSRF protection**: Required if using cookies for session/token storage without `SameSite=Strict`.

## Related Skills
- `secrets-scanning`: To ensure secrets used in auth aren't leaked.
- `fastapi-patterns` / `express-patterns`: For framework-specific implementation.