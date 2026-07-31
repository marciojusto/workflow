# MMH-1483 — Validation Report

**Ticket:** MMH-1483  
**Date:** 2026-07-03  
**Validator:** Agent (self-validation + manual review)  
**Status:** ⚠️ PARTIAL PASS

---

## Executive Summary

Backend changes are complete, committed, and all tests pass. Frontend branch contains the intended refactor but still has two functional bugs in `financing.actions.ts`:
1. `quotationTemplate` is sent on every normal calculation
2. `downpayment` scalar delta is sent at payload root instead of `financingAdjustment`

These bugs mean the financing tab downPayment blur does not currently trigger a correct MMP calculation.

---

## Acceptance Criteria Evidence

| AC | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| MMH1483-01 | Extract downpayment from delta → financingAdjustment | ❌ FAIL | `financing.actions.ts` still sends `{ downpayment: "1000" }` at root |
| MMH1483-02 | No downpayment at root | ❌ FAIL | Same as above |
| MMH1483-03 | No QT for normal calc | ❌ FAIL | `resolveCalculationPayload` returns `quotationTemplate` in default case |
| MMH1483-04 | QT only for bareme change | ❌ FAIL | Same as above |

**Backend-only ACs (implicit):**
| Requirement | Status | Evidence |
|-------------|--------|----------|
| Backend creates synthetic service for downPayment | ✅ PASS | `PayloadBuilderTest.firstCalculatePayload_whenFinancingAdjustmentProvided` |
| Synthetic choice has only id + isSelected | ✅ PASS | `PayloadBuilderTest.createSyntheticService_withDownpayment` asserts `label == null` |

---

## Test Results

### deal-bs
```
Tests run: 946, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

### hyperfront
```
npm run build
[nitro] ✔ You can preview this build using node .output/server/index.mjs
BUILD SUCCESS
```

### Manual / E2E
- Not executed — pending frontend fix.

---

## Discrimination Sensor

| Fault Injected | Expected Failure | Detected? |
|----------------|------------------|-----------|
| Remove `SYNTHETIC_CHOICE_ID` from downPayment | Backend test fails | ✅ Yes — `PayloadBuilderTest.withDownpayment` |
| Send `label` in synthetic choice | Backend test fails | ✅ Yes — `assertNull(label)` |
| Omit `financingAdjustment` from payload | No synthetic service created | ⚠️ Not covered by automated test yet |

---

## Gaps

1. Frontend `_buildCalculationPayload` needs refactor to fix ACs MMH1483-01 to MMH1483-04.
2. No automated frontend test exists for the POST payload shape.
3. Manual E2E on financing tab downPayment blur pending.

---

## Diff Range

- **deal-bs:** `develop...feature/MMH-1483`
- **hyperfront:** `develop...feature/MMH-1483`

## Recommendation

Complete frontend fix in `features/financing/stores/financing.actions.ts` before considering the ticket validated.
