---
name: api-security
description: Secure APIs with authn/z, validation, rate limits, error hygiene, CORS, and logging.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: security
  triggers: ["API endpoint work", "Public API exposure", "Auth middleware"]
---

# API Security

Essential security controls for building robust API endpoints.

## When to Activate

- Designing new API endpoints.
- Reviewing existing API routing and middleware.
- Configuring public-facing services.

## Core Controls

### 1. Authentication & Authorization (Authn/Authz)
- **Always Authenticate**: Unless explicitly public, endpoints must verify identity.
- **Always Authorize**: Verify the authenticated user has permission to access the specific resource requested (IDOR prevention).
- **JWT Hygiene**: Validate signature, expiration (`exp`), and issuer (`iss`). Do not store sensitive data in the token payload.

### 2. Input Validation
- **Never Trust the Client**: Validate all incoming data (headers, query parameters, body).
- **Use Schemas**: Define strict expected formats (e.g., using Zod, Pydantic, Joi).
- **Type Checking**: Ensure numbers are numbers, strings are within length limits.

### 3. Rate Limiting & Throttling
- **Protect Resources**: Prevent abuse and DDoS by limiting requests per IP or user token.
- **Endpoint Specific Limits**: Login or password reset endpoints need much stricter limits than read endpoints.

### 4. Error Handling Hygiene
- **No Stack Traces**: Never expose internal stack traces or database errors to the client.
- **Generic Messages**: Use generic error messages for sensitive operations (e.g., "Invalid credentials" instead of "User not found").
- **Consistent Structure**: Return a standardized error format.

### 5. CORS (Cross-Origin Resource Sharing)
- **Strict Origins**: Specify exact allowed origins. Do NOT use `Access-Control-Allow-Origin: *` for authenticated APIs.
- **Limit Methods**: Only allow necessary HTTP methods (GET, POST).

## Example Implementation (Express.js)

```javascript
// 1. Rate Limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// 2. Schema Validation (Zod)
const userSchema = z.object({
  email: z.string().email(),
  age: z.number().min(18)
});

app.post('/api/users', authMiddleware, (req, res) => {
  // Validate input
  const result = userSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ error: "Invalid input data" });
  }

  // 3. Authorization Check
  if (!req.user.isAdmin) {
    return res.status(403).json({ error: "Forbidden" });
  }

  // Handle logic...
});

// 4. Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.stack); // Log internally
  res.status(500).json({ error: "Internal Server Error" }); // Generic response
});
```

## Security Checklist

Before exposing an endpoint:
- [ ] Authentication is required (or explicitly public).
- [ ] Authorization checks ownership/permissions.
- [ ] Input data is validated against a strict schema.
- [ ] Rate limiting is applied.
- [ ] HTTPS is enforced.
- [ ] Errors do not leak internal system details.
