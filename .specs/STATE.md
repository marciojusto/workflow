# Project State — MMH-1483

## Active Decisions (AD-NNN)

### AD-001 — Synthetic Choice ID Hardcoded
**Decision:** Use hardcoded `SYNTHETIC_CHOICE_ID = "400228"` for synthetic service choices (downPayment, tradeIn, ecoBonus).

**Rationale:**
- ProductConfig.xml shows ComponentMapping `<id>400228</id>` for "Include" choice on Trade-in Value and ECO Bonus services.
- IDs are stable MMP configuration values.
- Avoids extra GET call to MMP just to resolve choice ID (KISS/YAGNI).

**Scope:** `deal-bs/src/main/java/com/mfs/mpp/integrationlayer/core/utils/PayloadBuilder.java`

**Confirmed by:** miles-expert investigation + ProductConfig.xml

---

### AD-002 — Backend Payload Structure is Correct; Fix is Frontend-Only
**Decision:** Do not modify `RequestCalculateDeal`, `PayloadBuilder`, or `DealServiceImpl` further for the downPayment-in-financing-tab issue.

**Rationale:**
- Backend already accepts `financingAdjustment.downpayment` and creates synthetic services correctly.
- The bug was that frontend sent `downpayment` at payload root and always sent `quotationTemplate`.

**Scope:** hyperfront `features/financing/stores/financing.actions.ts`

---

### AD-003 — Remove Label from Synthetic Service Choices
**Decision:** Synthetic service choices contain only `id` and `isSelected`; no `label` field.

**Rationale:**
- Architect confirmed `label` is not in the MMP API request for choices.
- Hardcoded `label: { translation: "SELECTED" }` does not exist in the API.

**Scope:** `PayloadBuilder.createSyntheticService()`

---

### AD-004 — QuotationTemplate Only on Bareme Change
**Decision:** Frontend must send `quotationTemplate` only when the user explicitly changes the bareme.

**Rationale:**
- Sending `quotationTemplate` on every calculation triggers QT Change in backend, which removes `financingAdjustment`/`productConfiguration`/`configOptions`.
- Normal tab-enter/field-blur calculations should not trigger QT Change.

**Scope:** hyperfront `_buildCalculationPayload()`

---

## Handoff Snapshot

**Ticket:** MMH-1483  
**Status:** Backend complete ✅ | Frontend partial ⚠️  
**Last updated:** 2026-07-03

### What is done
- `deal-bs`:
  - `FinancingAdjustmentDTO` created (downpayment, tradeInValue, ecoBonus)
  - `RequestCalculateDeal` uses `financingAdjustment`
  - `DealServiceImpl.calculateDeal` simplified to single MMP call
  - `PayloadBuilder` creates synthetic services with choice ID
  - Label removed from synthetic choices
  - Redundant condition removed from `renameDurationAndDistance`
  - Tests updated and passing (946 tests, 0 failures)
  - Committed to `feature/MMH-1483`

- `hyperfront` branch `feature/MMH-1483`:
  - `types/types.ts`: `FinancingAdjustment` interface added (currently unused)
  - `financing.shared.ts`: `buildFinancingAdjustment()` extracted, `attachFinancialInputs()` refactored
  - `assets.ts` / `assetService.ts`: use `financingAdjustment`
  - `calculations.post.tsx`: removed manual ecoBonus injection, added `preserveField()`
  - `financing.actions.ts`: still sends `quotationTemplate` by default and `downpayment` at root (needs fix)

### What is pending
- Fix `hyperfront/features/financing/stores/financing.actions.ts` `_buildCalculationPayload()`:
  1. Extract `downpayment`/`tradeInValue` from delta payload
  2. Build context-aware payload (no `quotationTemplate` unless bareme changes)
  3. Force `attachFinancialInputs` when financial delta is present
- Remove unused `FinancingAdjustment` interface or start using it
- Remove unused `_buildConfigOptionsFromFinancing` method
- Run E2E/manual tests on financing tab downPayment blur

### Blockers
- None

### Notes
- Physical worktree `projects/hyperfront-worktree` contains MMH-1483 content but git worktree registry is stale (path moved from `mobilize/hyperfront-worktree` to `mobilize/projects/hyperfront-worktree`).
- Need `git worktree repair` or recreate worktree when resuming frontend work.
