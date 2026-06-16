---
name: python-patterns
description: Reference for modern Python patterns including type hints, dataclasses, async/await, and context managers.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: reference
triggers:
  - "python typing"
  - "python patterns"
  - "dataclass"
---

# Python Patterns

Best practices for writing modern, idiomatic Python (3.10+).

## When to Activate
- Writing or refactoring Python code.
- Implementing type hints or updating legacy code to modern standards.
- Creating data structures or managing resources.

## How It Works

### Type Hints and Protocols
Use strict typing for better tooling and readability. Use `Protocol` for structural subtyping (duck typing).

```python
from typing import Protocol, Iterator
from dataclasses import dataclass

class Logger(Protocol):
    def log(self, message: str) -> None: ...

class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"LOG: {message}")

# Function accepts anything that implements log()
def process_data(logger: Logger) -> None:
    logger.log("Processing started")
```

### Dataclasses
Use `@dataclass` instead of boilerplate `__init__` methods for classes primarily storing data.

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True) # frozen=True makes it immutable
class User:
    id: int
    name: str
    roles: list[str] = field(default_factory=list) # Mutable defaults must use default_factory
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### Context Managers
Always use context managers (`with`) for resources that need cleanup (files, connections, locks).

```python
# Standard usage
with open("data.txt", "r") as f:
    data = f.read()

# Custom context manager using contextlib
from contextlib import contextmanager

@contextmanager
def db_transaction():
    db.begin()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

with db_transaction() as db:
    db.execute("UPDATE users SET active = 1")
```

### Async / Await
Use `asyncio` for I/O bound concurrency.

```python
import asyncio
import httpx

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

async def main():
    # Run multiple async operations concurrently
    urls = ["http://api1.com", "http://api2.com"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(results)
```

## Verification Steps
1. Run `mypy` or `pyright` to verify strict type correctness.
2. Run `pytest` to ensure functionality.
3. Ensure formatting with `black` and `isort` (or `ruff`).

## Common Pitfalls
- **Mutable Default Arguments**: `def func(items=[])` creates a single list shared across all calls. Use `def func(items=None)` and initialize inside the function.
- **Ignoring Type Errors**: Suppressing type checker errors with `# type: ignore` instead of fixing the underlying signature.
- **Mixing Sync/Async**: Calling synchronous blocking functions (like `time.sleep()`) inside an `async def` function blocks the entire event loop. Use `asyncio.sleep()` instead.

## Related Skills
- `fastapi-patterns`: For applying these Python patterns within web APIs.