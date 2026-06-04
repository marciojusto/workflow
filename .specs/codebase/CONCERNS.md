# Concerns

## Tech Debt

### bsClient duplicates fetch logic

**Location:** `server/services/bsClient.ts`
**Issue:** Each method duplicates retry/error handling boilerplate. Could be extracted to a base client class or use an interceptor pattern.
**Fix:** Extract `bsFetch` base utility with automatic retry, logging, and error transformation.
**Priority:** Low

### Inconsistent error responses

**Location:** Multiple `server/api/*.ts` handlers
**Issue:** Some handlers return `{success: true, data}`, others return raw data directly. No consistent error shape.
**Fix:** Adopt the pattern from the Error Handling section in AGENTS.md (use `createError` consistently).
**Priority:** Medium

## Test Coverage Gaps

### Regression test suite

**Location:** `playwright/tests/regression/`
**Issue:** Template exists but no real regression tests generated yet. Trace-to-Playwright pipeline is built but not yet operational (needs agent/skill prompt updates).
**Fix:** Complete agent updates to wire test_trace output → trace-to-playwright.py → generated spec.

### No unit tests for Pinia stores

**Location:** `features/*/stores/`
**Issue:** Stores have no test coverage. Business logic in store actions is untested.
**Fix:** Add Vitest tests for critical stores (auth, deal state).
**Priority:** Low

## Fragile Areas

### DPP popup handling

**Location:** E2E tests
**Issue:** Data Privacy popup appears unpredictably during deal creation. Playwright tests must handle it (click "sending by email").
**Fix:** `DealCreatePage.createAnonymousDeal()` already handles it, but dependent on DOM structure.

### Proposal phase timing

**Location:** Proposal workflow
**Issue:** Proposal phase button enabled only after clicking "send secci". Race condition in E2E tests if secci hasn't completed.
**Fix:** Add explicit `waitFor` in page objects after secci click.

## Performance

- No bundle analysis configured
- No lazy loading audit for heavy pages
- MongoDB queries in server/api/ handlers not indexed
