# Testing Infrastructure

## Test Frameworks

**Unit/Integration:** Vitest (via `@nuxt/test-utils`)
**E2E:** Playwright (`playwright/` dir)
**Coverage:** Not configured

## Test Organization

**Unit:** `tests/` directory at project root
**E2E:** `playwright/tests/` with page objects in `playwright/tests/page-objects/`
**Regression:** `playwright/tests/regression/`

## Testing Patterns

### Unit Tests

**Approach:** Vitest with Nuxt test utils. Tests for server API handlers in `tests/server/`.
**Location:** `tests/` (e.g. `tests/server/ping.spec.ts`)
**Command:** `npm test` or `npx vitest run`

### E2E Tests

**Approach:** Playwright with page objects. `beforeEach` creates deal data. Tests validate ACs. `afterEach` takes screenshots.
**Location:** `playwright/tests/` (specs) and `playwright/tests/page-objects/` (page objects)
**Command:** `npx playwright test`

## Test Execution

**Commands:**
- Unit: `npm test` or `npx vitest run`
- Single unit: `npx vitest run tests/server/ping.spec.ts`
- E2E: `cd playwright && npx playwright test`
- E2E single: `npx playwright test tests/regression/template.spec.ts`

## Test Coverage Matrix

| Code Layer | Required Test Type | Location Pattern | Run Command |
|---|---|---|---|
| Server API | Unit | `tests/server/*.spec.ts` | `npx vitest run` |
| Page Objects | E2E | `playwright/tests/page-objects/*.ts` | `npx playwright test` |
| UI Components | E2E | `playwright/tests/*.spec.ts` | `npx playwright test` |
| Regression | E2E | `playwright/tests/regression/*.spec.ts` | `npx playwright test` |

## Gate Check Commands

| Gate Level | When to Use | Command |
|---|---|---|
| Quick | After tasks with unit tests only | `npx vitest run` |
| Full | After tasks with E2E | `cd playwright && npx playwright test` |
| Build | After phase completion | `npm run build && cd playwright && npx playwright test` |
