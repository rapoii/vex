---
name: fastapi-patterns
description: Reference for FastAPI patterns including dependencies, middleware, background tasks, and Pydantic models.
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: reference
triggers:
  - "fastapi"
  - "pydantic"
  - "fastapi-patterns"
---

# FastAPI Patterns

Best practices for building robust APIs using FastAPI and Pydantic in Python.

## When to Activate
- Writing or reviewing FastAPI endpoints.
- Designing Pydantic schemas.
- Implementing dependency injection or middleware in Python APIs.

## How It Works

### Pydantic Models (v2)
Separate input schemas from output schemas.

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    
    # Enable ORM mode for DB compatibility
    model_config = {"from_attributes": True}
```

### Dependency Injection
Use `Depends` to inject database sessions, users, or logic into endpoints. This makes testing easy.

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Dependency function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

# Endpoint using dependencies
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_in_db(db, user)
```

### Background Tasks
Offload slow operations (email sending, processing) from the request response cycle.

```python
from fastapi import BackgroundTasks

def write_notification(email: str, message: str):
    with open("log.txt", mode="a") as email_file:
        email_file.write(f"notification for {email}: {message}")

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

### Exception Handling
Centralize error handling with custom exception handlers.

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ItemNotFoundError(Exception):
    pass

@app.exception_handler(ItemNotFoundError)
async def not_found_exception_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": "Item not found in database"},
    )
```

## Verification Steps
1. Run `pytest` with `TestClient` to verify endpoints. Dependency overrides (`app.dependency_overrides`) make testing simple.
2. Check the auto-generated Swagger UI (`/docs`) to ensure schemas and validation errors are correctly documented.
3. Validate Pydantic v2 usage (e.g., using `model_dump()` instead of `dict()`).

## Common Pitfalls
- **Blocking the Event Loop**: Calling synchronous blocking code (like `requests.get` or heavy CPU tasks) inside `async def` endpoints. Use standard `def` for synchronous code, or use `await` with async libraries (like `httpx`).
- **Leaking DB Connections**: Failing to use `yield` and `finally` in database dependencies, causing connection pool exhaustion.
- **Returning DB Models Directly**: Always return Pydantic models (using `response_model`) to strip sensitive DB fields (like passwords) before serialization.

## Related Skills
- `python-patterns`: General Python language features used alongside FastAPI.