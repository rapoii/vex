---
name: tdd-workflow
description: Drive RED/GREEN/REFACTOR loops with regression-first tests and explicit validation gates.
argument-hint: "[scope | file | goal]"
metadata:
  origin: VEX
  category: workflow
  triggers: ["New feature with clear behavior", "Bug fix needing regression coverage", "Refactor where behavior must remain stable"]
---

# TDD Workflow

Drive RED/GREEN/REFACTOR loops with regression-first tests and explicit validation gates.

## When to Activate

- New feature with clear behavior
- Bug fix needing regression coverage
- Refactor where behavior must remain stable
- Continuing from a `/plan` output or another `*.plan.md` implementation plan

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements
- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. Test Types

#### Unit Tests
- Individual functions and utilities
- Component logic

#### Integration Tests
- API endpoints
- Database operations

#### E2E Tests
- Critical user flows
- Complete workflows

## TDD Workflow Steps

### Step 1: Write User Journeys

If a `*.plan.md` file was provided, extract the user journeys and acceptance criteria from that plan first. Only write new journeys for gaps the plan does not cover.

```
As a [role], I want to [action], so that [benefit]
```

### Step 2: Generate Test Cases
For each user journey, create comprehensive test cases:

```typescript
describe('Feature', () => {
  it('returns expected output', async () => {
    // Test implementation
  })

  it('handles edge cases', async () => {
    // Test edge case
  })
})
```

### Step 3: Run Tests (They Should Fail)
```bash
npm test # or pytest, go test, etc.
# Tests should fail - we haven't implemented yet
```

This step is mandatory and is the RED gate for all production changes. Do not edit production code until this RED state is confirmed.

### Step 4: Implement Code
Write minimal code to make tests pass.

### Step 5: Run Tests Again
```bash
npm test
# Tests should now pass
```

Rerun the same relevant test target after the fix and confirm the previously failing test is now GREEN.

### Step 6: Refactor
Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance

### Step 7: Verify Coverage
```bash
npm run test:coverage # or relevant coverage command
# Verify 80%+ coverage achieved
```

## Testing Patterns

### React / Jest Unit Test
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

### Python / Pytest API Test
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/items/", json={"name": "Test Item"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
```

### Go Table-Driven Test
```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"mixed", -1, 2, 1},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Errorf("Add() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

## Common Testing Mistakes to Avoid

### FAIL: WRONG: Testing Implementation Details
```typescript
// Don't test internal state
expect(component.state.count).toBe(5)
```

### PASS: CORRECT: Test User-Visible Behavior
```typescript
// Test what users see
expect(screen.getByText('Count: 5')).toBeInTheDocument()
```

### FAIL: WRONG: Brittle Selectors
```typescript
// Breaks easily
await page.click('.css-class-xyz')
```

### PASS: CORRECT: Semantic Selectors
```typescript
// Resilient to changes
await page.click('button:has-text("Submit")')
await page.click('[data-testid="submit-button"]')
```

## Success Metrics

- 80%+ code coverage achieved
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution
- Tests catch bugs before production
