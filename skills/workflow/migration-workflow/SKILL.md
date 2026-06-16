---
name: migration-workflow
description: Best practices for database schema and data migrations (Alembic, Flyway, zero-downtime).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: workflow
triggers:
  - "database migration"
  - "schema change"
  - "zero downtime db"
  - "migration-workflow"
---

# Migration Workflow

Safely managing database schema changes and data migrations, ensuring zero downtime and backward compatibility.

## When to Activate
- Task involves adding columns, altering tables, or dropping data in SQL databases.
- Writing Alembic, Flyway, Prisma, or golang-migrate scripts.
- Managing API versioning and deprecation.

## How It Works

### Zero-Downtime Database Migrations
Deployments (where both V1 and V2 of code run simultaneously) require database changes to be backward compatible.

**The Expand-Contract Pattern:**

*Phase 1: Expand*
1. Add the new column/table (nullable or with default).
2. Code V2 reads from new (fallback to old), writes to both.
3. Deploy Code V2.

*Phase 2: Migrate Data*
1. Run a background script to backfill old rows into the new column.

*Phase 3: Contract*
1. Code V3 only reads/writes to new column.
2. Deploy Code V3.
3. Drop the old column.

### Example: Alembic (Python/SQLAlchemy)
Never alter a column type directly if it locks the table for a long time.

```python
# GOOD: Adding a nullable column
def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))

def downgrade():
    op.drop_column('users', 'phone_number')

# BAD: Adding a non-nullable column without a default (will fail on existing data)
# op.add_column('users', sa.Column('phone_number', sa.String(), nullable=False))
```

### Data Migrations
Separate schema migrations from data migrations. Schema migrations run fast; data migrations (backfills) can take hours and should be processed in batches.

```python
# Batching data migration to avoid locking the table
def backfill_data(batch_size=1000):
    last_id = 0
    while True:
        rows = db.execute(f"SELECT id FROM users WHERE id > {last_id} LIMIT {batch_size}")
        if not rows:
            break
        # Process rows and update
        last_id = rows[-1].id
        time.sleep(0.1) # Yield to other queries
```

### API Versioning
When changing API responses, use versioning instead of breaking clients.

```typescript
// /api/v1/users -> Returns { first_name, last_name }
// /api/v2/users -> Returns { name: "First Last" }
```

## Verification Steps
1. Run the migration down, then up (`db migrate down && db migrate up`) locally to ensure the downgrade path works.
2. Query the database to ensure locks won't block production traffic (`CREATE INDEX CONCURRENTLY` in Postgres).
3. Ensure application code V1 doesn't crash when running against schema V2.

## Common Pitfalls
- **Exclusive Locks**: Commands like `ALTER TABLE` or adding indices without `CONCURRENTLY` can lock production tables for minutes/hours, causing outages.
- **Renaming Columns**: Renaming a column instantly breaks any running code expecting the old name. Use the Expand-Contract pattern instead.
- **Testing on empty DBs**: Migrations that work on an empty local DB often fail or timeout on a 100GB production table. Test against a snapshot or realistic data volume.

## Related Skills
- `deployment-flow`: Managing the rollout of code that accompanies migrations.
- `release-workflow`: Coordinating major version bumps.

## Pipeline

**Previous:** (migration requirement) — schema or data change starts migration flow
**Next:** [code-review-flow](../code-review-flow/SKILL.md) — review diffs with severity ordering and actionable fixes