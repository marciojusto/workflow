# MMH-1544 — Company & Seller Filter Missing in BFF Endpoints

**Type:** Bug (no Acceptance Criteria — using ticket description as main task)

## 1. Task Description

The `x-brokers` header (company filter) and `x-seller-id` header (seller filter) are already
parsed and applied in the main list endpoints (`deals.get.ts`, `deal-list.get.tsx`), but are
**missing** in three BFF endpoints. Additionally, the parsing logic is currently **duplicated**
across those 2 existing endpoints.

**Solution:** Extract the access control parsing into a shared utility
(`server/utils/accessControl.ts`) and use it in all 5 endpoints, eliminating duplication.

## 2. Steps / Implementation

### Step 0 — Create shared utility `server/utils/accessControl.ts`

**New file:** `server/utils/accessControl.ts`

```typescript
import { getHeader } from "h3";

/**
 * Builds an access control filter from request headers.
 * Combines company (x-brokers → dealership_id) and
 * seller (x-seller-id → seller_id) filters.
 */
export function buildAccessFilter(event: any): Record<string, any> {
  const filter: Record<string, any> = {};

  const brokers = getHeader(event, "x-brokers");
  const brokersList = brokers?.split(",").map((id) => id.trim());
  if (brokersList?.length) filter.dealership_id = { $in: brokersList };

  const sellerId = getHeader(event, "x-seller-id")?.trim();
  if (sellerId) filter.seller_id = sellerId;

  return filter;
}
```

**Also refactor existing endpoints to use it:**
- `server/api/deals.get.ts` — replace inline parsing with `buildAccessFilter(event)`
- `server/api/deal-list.get.tsx` — replace inline parsing with `buildAccessFilter(event)`

### Step 1 — Company & Seller filter on `/api/deals/[id].get.ts` (RQ-001)

**File:** `server/api/deals/[id].get.ts`

**Changes:**
1. Import `buildAccessFilter` from `../../utils/accessControl`
2. Add `const accessFilter = buildAccessFilter(event);` after getting db
3. Spread `...accessFilter` into **both** `findOne` queries:
   - `db.collection('deal').findOne({ _id: new ObjectId(id), ...accessFilter })`
   - `db.collection('deal').findOne({ miles_sales_quote_id: id, ...accessFilter })`

**Rationale:** Shared utility eliminates duplication. If deal belongs to another company/seller, `findOne` returns null → 404.

### Step 2 — Company & Seller filter on `/api/dashboard/stats.get.ts` (RQ-002)

**File:** `server/api/dashboard/stats.get.ts`

**Changes:**
1. Import `buildAccessFilter` from `../../utils/accessControl`
2. Rename `_event` parameter to `event` (needed to pass to `buildAccessFilter`)
3. Add `const accessFilter = buildAccessFilter(event);` after the db check
4. Spread `...accessFilter` into **all 3** `countDocuments` calls:
   - `db.collection("deal").countDocuments({ ...accessFilter })` (totalDeals)
   - `db.collection("deal").countDocuments({ $or: [...], ...accessFilter })` (thisWeekCount)
   - `db.collection("deal").countDocuments({ $or: [...], ...accessFilter })` (lastWeekCount)
   - `simulationsActived`, `totalUsers`, `refinanced` remain hardcoded `0`

**Rationale:** Shared utility. Empty filter object = no scoping (all data visible).

### Step 3 — Company & Seller filter on `/api/deals/pick-list.post.ts` (RQ-003)

**File:** `server/api/deals/pick-list.post.ts`

**Changes:**
1. Import `buildAccessFilter` from `../../utils/accessControl`
2. Add `const accessFilter = buildAccessFilter(event);` after reading the body
3. After the filter map loop (line 41), merge in access filters:
   ```typescript
   Object.assign(f, accessFilter);
   ```

**Rationale:** Merges both filters into existing `f` via `Object.assign`, preserving request body filters.

## 3. RAG Materials Used

- `.specs/features/MMH-1544/spec.md` — Full specification document
- `server/api/deals.get.ts` — Reference pattern (will be refactored to use shared utility)
- `server/api/deal-list.get.tsx` — Reference pattern (will be refactored to use shared utility)
- `server/api/deals/[id].get.ts` — Target for RQ-001
- `server/api/dashboard/stats.get.ts` — Target for RQ-002
- `server/api/deals/pick-list.post.ts` — Target for RQ-003

## 4. RAG Materials NOT Used

- **None** — all provided materials were directly relevant.

## 5. Code Principles Adherence

### DRY — Don't Repeat Yourself
- **Key improvement:** Creates `server/utils/accessControl.ts` — a shared utility used by all 5 endpoints.
- Eliminates duplication: the same parsing logic currently exists in `deals.get.ts` and `deal-list.get.tsx`.
- The 3 new endpoints plus the 2 existing ones all call a single function.

### KISS — Keep It Simple, Stupid
- The utility is a single pure function (12 lines) with no dependencies beyond `h3`.
- Each endpoint change is 1–3 lines (import + call + spread).
- No new types, classes, or abstractions.

### YAGNI — You Aren't Gonna Need It
- Only the functionality currently needed: parse 2 headers, return a filter object.
- No middleware, no generic auth framework, no plugin system.
- The existing endpoints are refactored only to use the shared function — no behavioural changes.

### SOLID — Single Responsibility
- `accessControl.ts` has one job: build an access filter from request headers.
- Each endpoint keeps its single responsibility (query a deal, compute stats, return pick-list values).
- Separation is cleaner: access control logic lives in one place, query logic in another.

### SoC — Separation of Concerns
- Access control logic extracted to `server/utils/` — separate from API handlers.
- No changes to frontend (`shared/utils/api.ts`), stores, components, or BFF proxy.
- Both headers are already injected and forwarded client-side.
