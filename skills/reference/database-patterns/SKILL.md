---
name: database-patterns
description: Implement robust database architectures including connection pooling, transaction safety, safe schema migrations, and repository patterns.
argument-hint: "[db-type | driver | pattern]"
metadata:
  origin: VEX
---

# Database Patterns

Use this skill to ensure database access is safe, scalable, and maintainable across application lifecycles.

## Triggers

- Setting up a new database connection or ORM.
- Writing schema migrations or DDL files.
- Implementing transactions spanning multiple operations.
- Application crashes due to connection exhaustion.
- Abstracting direct SQL queries behind a repository layer.

## Inputs To Inspect

- Connection string configuration (`.env`).
- Database client initialization (`db.ts`, `prisma.ts`, `session.py`).
- Migration files (`migrations/`, `schema.prisma`).
- Business logic containing sequential database writes.

## Core Patterns

### 1. Connection Pooling

Never open a new connection per request. Manage a pool.

**Node.js / pg:**
```typescript
import { Pool } from 'pg';

// Initialize ONCE at module level, reuse globally
export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20, // Max concurrent connections
  idleTimeoutMillis: 30000,
});

// Use the pool
const result = await pool.query('SELECT * FROM users');
```

*Serverless note:* In AWS Lambda or Vercel, use a proxy like PgBouncer or Prisma Accelerate to prevent connection exhaustion.

### 2. Transaction Safety

Wrap multiple related writes in a transaction to prevent partial state on failure.

**Prisma:**
```typescript
await prisma.$transaction(async (tx) => {
  // 1. Deduct balance
  const account = await tx.account.update({
    where: { id: senderId },
    data: { balance: { decrement: amount } }
  });

  if (account.balance < 0) throw new Error('Insufficient funds');

  // 2. Add to receiver
  await tx.account.update({
    where: { id: receiverId },
    data: { balance: { increment: amount } }
  });
});
```

### 3. Safe Migrations

Never alter production tables manually. Use migration scripts.
Never lock a large table with DDL commands.

```sql
-- ❌ BAD: Locks table while rewriting all rows
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- ✅ GOOD: Fast, no rewrite (Postgres 11+)
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;

-- ❌ BAD: Blocks writes during index creation
CREATE INDEX idx_email ON users(email);

-- ✅ GOOD: Builds index without blocking writes
CREATE INDEX CONCURRENTLY idx_email ON users(email);
```

### 4. The Repository Pattern

Isolate SQL/ORM logic from business/HTTP logic.

```typescript
// UserRepository.ts
export class UserRepository {
  constructor(private db: Pool) {}

  async findActiveUsers(): Promise<User[]> {
    const { rows } = await this.db.query(
      'SELECT id, email FROM users WHERE status = $1', 
      ['active']
    );
    return rows;
  }
}

// Controller.ts - Knows nothing about SQL
const users = await userRepository.findActiveUsers();
```

## Common Pitfalls

- String concatenation for SQL queries (SQL Injection). Always use parameterized queries (`$1, $2` or `?`).
- Failing to release connections back to the pool after a manual transaction block errors out.
- Performing long-running logic (e.g., calling external APIs) inside an open database transaction, locking rows and exhausting the pool.
- Deploying code that relies on a new database column before the migration has run.

## Done Criteria

- Database connection uses a bounded pool.
- Multi-step writes are atomic via transactions.
- Schema changes are written as reversible migration scripts.
- Queries use parameters, never string interpolation.
