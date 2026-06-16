---
name: test-automation
description: Configure test frameworks (Jest, Vitest, Pytest), runners, coverage reporting, and CI integration to maintain 80%+ coverage requirements reliably.
argument-hint: "[framework | scope | integration]"
metadata:
  origin: VEX
---

# Test Automation

Use this skill when setting up, fixing, or optimizing test frameworks, coverage reporting, or test execution pipelines.

## Triggers

- User asks to set up testing, Jest, Vitest, Pytest, or Cypress.
- Tests are flaky, slow, or failing randomly in CI.
- Need to configure coverage reports to meet the 80% requirement.
- Adding integration or E2E tests alongside unit tests.

## Inputs To Inspect

- `jest.config.js`, `vitest.config.ts`, `pytest.ini`, or `playwright.config.ts`.
- `package.json` test scripts.
- CI workflow files (to see how tests are run).
- Source directories and file naming conventions (`*.test.ts`, `*_test.py`).

## Test Automation Strategy

1. Separate unit tests (fast, mocked) from integration/E2E tests (slow, real dependencies).
2. Configure a fast runner (Vitest for JS/TS, Pytest for Python).
3. Set up coverage reporting enforcing the 80% minimum.
4. Ensure tests run deterministically regardless of order.
5. In CI, fail fast and upload coverage artifacts.

## Vitest Setup (TypeScript/React)

Vitest is preferred over Jest for modern Vite/TS projects due to speed and native ESM.

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'html'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      },
      exclude: [
        'node_modules/',
        'dist/',
        'test/',
        '**/*.d.ts'
      ]
    }
  }
})
```

## Pytest Setup (Python)

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
markers =
    integration: mark test as an integration test requiring external services
```

## Playwright Setup (E2E)

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## CI Integration

Add to `.github/workflows/test.yml`:

```yaml
      - run: npm run test:coverage
      
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report
          path: coverage/
```

## Verification Commands

```bash
# Run unit tests with coverage
npm run test -- --coverage

# Run specific file only
npm run test -- path/to/file.test.ts

# Run Pytest with coverage
pytest --cov
```

## Common Pitfalls

- Testing implementation details (private methods) instead of behavior/public APIs.
- Sharing state between tests (global variables, un-cleared database records).
- Using arbitrary `sleep()` in E2E tests instead of waiting for locators.
- Running E2E tests on every commit; reserve them for PRs or nightly builds if slow.
- Missing timezone or locale mocks causing tests to fail on different machines.
- Ignoring coverage exclusions, requiring 80% coverage on configuration files or types.

## Done Criteria

- Command `npm test` runs all unit tests.
- Command `npm run test:coverage` fails if coverage drops below 80%.
- Tests do not leak state to each other.
- CI pipeline catches test failures and blocks merges.
