---
name: typescript-patterns
description: Reference for TypeScript patterns including generics, discriminated unions, template literals, and utility types.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: reference
triggers:
  - "typescript"
  - "ts types"
  - "typescript-patterns"
---

# TypeScript Patterns

Advanced and idiomatic TypeScript patterns for strict, robust web applications.

## When to Activate
- Writing or reviewing TypeScript code.
- Designing complex data models or API responses.
- Fixing `any` types or type narrowing issues.

## How It Works

### Discriminated Unions
The safest way to handle varied state or responses. Use a common literal property (the "discriminator") to narrow types.

```typescript
type ApiResponse = 
  | { status: "loading" }
  | { status: "success"; data: User[] }
  | { status: "error"; message: string };

function handleResponse(res: ApiResponse) {
  // TypeScript knows 'res' structure based on the 'status' check
  if (res.status === "success") {
    console.log(res.data); // OK
  } else if (res.status === "error") {
    console.error(res.message); // OK
  }
}
```

### Utility Types
Transform existing types instead of duplicating them.

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  role: "admin" | "user";
}

// Omit properties
type UserCreateInput = Omit<User, "id">;

// Pick properties
type UserSummary = Pick<User, "id" | "name">;

// Make all properties optional
type UserUpdate = Partial<User>;

// Extract from union
type AdminRole = Extract<User["role"], "admin">;
```

### Type Guards (User-Defined)
Narrow down `unknown` or wide types safely.

```typescript
interface ApiError {
  code: number;
  message: string;
}

// Type guard function
function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    "message" in error
  );
}

try {
  await fetchUser();
} catch (error) {
  if (isApiError(error)) {
    console.log(error.code); // Safe to access
  }
}
```

### Template Literal Types
Create precise types by composing strings.

```typescript
type Color = "red" | "blue";
type Size = "small" | "large";

// Generates: "text-red-small" | "text-red-large" | "text-blue-small" | "text-blue-large"
type TextStyle = `text-${Color}-${Size}`;

// Useful for event names or routing paths
type EventName = `${Color}Clicked`;
```

## Verification Steps
1. Run `tsc --noEmit` to ensure type checks pass across the project.
2. Enable `strict: true` in `tsconfig.json` to enforce null checks and prevent implicit `any`.
3. Check IDE hover states to confirm inferred types match expectations.

## Common Pitfalls
- **Using `any`**: Defeats the purpose of TypeScript. Use `unknown` if the shape is truly unknown, then narrow it with type guards or validation libraries (like Zod).
- **Overusing `as` (Type Assertions)**: `const user = data as User` lies to the compiler. It forces the type without checking runtime structure. Use validation schemas instead.
- **Enum Issues**: TypeScript `enum` creates runtime code and has quirks. Prefer const objects or string unions (`type Role = "ADMIN" | "USER"`).

## Related Skills
- `react-patterns`: Applying TypeScript patterns to React props and state.
- `fastapi-patterns`: For API backend typing that pairs well with frontend TS interfaces.