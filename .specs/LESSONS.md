# Lessons Learned — MMH-1483

## Technical Lessons

### 1. Synthetic MMP Services Require Choice ID, Not Label
When creating synthetic services for the MMP `/sales-quotes/{id}/actions/calculations` endpoint, the choice object must contain `id` (matching the ProductConfig.xml ComponentMapping) and `isSelected`. The `label` field is not part of the request contract and should not be sent.

**Evidence:** Architect review + `PayloadBuilderTest` assertions.

---

### 2. MMP Response Structure is Independent of Request Path
Whether the request uses `quotationTemplate` (QT Change) or `productConfiguration` (Services scenario), the MMP response is always the same `CalculateSalesQuoteResponse` with a full `salesQuote`.

**Implication:** Frontend response handling (`buildCalculateResponse`) does not need branching based on request type.

---

### 3. Frontend Delta Payloads Must Map to Backend DTO Fields
Sending a field name from the UI directly as a root JSON key (`{ downpayment: "1000" }`) only works if the backend DTO has that root field. `RequestCalculateDeal` does not have `downpayment` at root — it has `financingAdjustment.downpayment`.

**Implication:** Financial field changes in the financing tab must be mapped to `financingAdjustment`, not sent as scalar deltas.

---

### 4. QuotationTemplate is a Bareme-Change Signal
The backend treats any payload with `quotationTemplate.quotationTemplateId` as a QT Change, which strips `financingAdjustment`, `productConfiguration`, and `configOptions`.

**Implication:** Only send `quotationTemplate` when the user actually changes the bareme. Tab-enter and field-blur calculations must omit it.

---

## Process Lessons

### 5. Verify Physical Worktree Content, Not Just Git Branch Output
When a worktree is moved, `git branch --show-current` inside the physical directory can return the wrong branch because the git registry is stale. Always verify content by diffing against the expected branch.

**Evidence:** `projects/hyperfront-worktree` physically contains MMH-1483 content despite `git branch` showing MMH-1517.

---

### 6. Dead Code Lurks in Type Definitions and Private Methods
Unused exported interfaces (`FinancingAdjustment` in `types/types.ts`) and private store methods (`_buildConfigOptionsFromFinancing`) are easy to miss. Explicit grep for usages is necessary.

