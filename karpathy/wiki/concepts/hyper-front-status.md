# HyperFront Status System
- **Original Source**: Codebase analysis (server/services/dealService.ts, server/plugins/mongoose.ts, scripts/data/matrix.csv)
- **Processing Date**: 2026-05-05
- **Tags**: #concept #hyper-front-status #matrix #deal-status
---

## Overview

`hyper_front_status` is a field stored in the MongoDB `deal` collection that represents the **user-facing status** of a deal/offer. It is the abstraction layer between raw Miles/Sofico backend statuses and the HyperFront UI.

## Data Source: Matrix Collection

The status is derived from a MongoDB collection called **`matrix`** which acts as a lookup table. It is seeded from `scripts/data/matrix.csv` via `scripts/insertMatrixData.cjs`.

### Matrix Structure

| Column | Type | Description |
|--------|------|-------------|
| `sales_quote_status` | Input | BS quote status name |
| `sales_quote_status_enum_id` | Input | BS quote status enum ID |
| `credit_application_status` | Input | BS credit application status |
| `credit_application_status_enum_id` | Input | BS credit application status enum ID |
| `pending_contract_status` | Input | BS pending contract status |
| `pending_contract_status_enum_id` | Input | BS pending contract status enum ID |
| `credit_decision` | Input | BS credit decision |
| `credit_decision_enum_id` | Input | BS credit decision enum ID |
| **`hyper_front_status`** | **Output** | **User-facing deal status** |
| **`hyper_front_action`** | **Output** | **Next action required** |
| **`overview_status`** | **Output** | **Dashboard grouping key** |

### Possible hyper_front_status Values
- Online simulation
- Pending simulation
- Pending proposal
- Pending Dealer / counter offer
- Pre-approved
- Under Study
- Approved
- Waiting for delivery
- Expired
- Canceled
- Rejected

## How It Gets Populated

### 1. Deal Creation (NOT set)
In `server/services/dealPayloadBuilder.ts`, the `buildDealPayload()` function creates the initial deal object but **does not include** `hyper_front_status`. It is intentionally left null.

### 2. Change Stream (TRIGGER)
In `server/plugins/mongoose.ts`, a MongoDB change stream watches the `deal` collection. On any insert/update, it calls:

```typescript
changeStream.on("change", (change) => processDealChange(change, collection, processingDeals));
```

### 3. Matrix Lookup (THE ACTUAL SET)
In `server/services/dealService.ts:554-591`, `updateDealFromMatrix(deal)`:

```typescript
const matrix = await db.collection("matrix").findOne(buildMatrixLookupFilter(deal));
if (matrix) {
  const updateFields = {
    overview_status: matrix.overview_status,
    hyper_front_status: matrix.hyper_front_status,
    hyper_front_action: matrix.hyper_front_action
  };
  await db.collection("deal").updateOne(
    { miles_sales_quote_id },
    { $set: updateFields }
  );
}
```

### 4. Expiration (SCHEDULED)
In `server/services/dealService.ts:593-647`, `expireDealsByPhaseDates()` runs daily via cron (`server/plugins/scheduler.ts`):

```typescript
const expiredUpdate = {
  hyper_front_status: "Expired",
  hyper_front_action: null,
  to_be_expired: true,
  last_update_time: new Date(),
};
```

### 5. Sync (MANUAL/API)
Endpoint `GET /api/sync/deals` calls `getDealsToUpdate()` which queries deals with status in `HYPER_FRONT_STATUSES_TO_SYNC` (currently only "Under Study") and syncs them from BS API.

## Preview (READ-ONLY)
Function `previewHyperFrontFromMatrix()` at `server/services/dealService.ts:501-552` simulates what status a deal would get without persisting — used to show users the resulting status before confirming actions.

## Data Flow Diagram
```
BS API (Miles/Sofico)
    │ returns quote statuses & enum IDs
    ▼
saveDealToDB() / Change Stream
    │ triggers updateDealFromMatrix()
    ▼
matrix collection lookup
    │ matches on status_enum_id + status_group_enum_id
    ▼
deal.hyper_front_status ← matrix.hyper_front_status
    │
    ▼
Frontend API response
    │ hyper_front_status sent verbatim
    ▼
offerStore.offerStatus = payload.hyper_front_status
    │
    ▼
OfferPreview.vue / Deal list
    │ displays raw value (no translation on value)
```

## Common Issues

### Missing hyper_front_status
Causes:
1. No matching matrix row for the deal's status combination
2. Change stream failed (server restart during creation)
3. Legacy deals created before matrix system existed
4. Direct DB inserts bypassing change stream

### "Cancelled" vs "Canceled"
- The matrix CSV had 10 rows with output "Cancelled" (British spelling)
- Changed to "Canceled" in CSV + re-seeded MongoDB via `insertMatrixData.cjs`
- Existing deals needed manual update: `db.deal.updateMany({ hyper_front_status: "Cancelled" }, { $set: { hyper_front_status: "Canceled" } })`

## Related Files
- `server/services/dealPayloadBuilder.ts` - Creates initial deal (no hyper_front_status)
- `server/services/dealService.ts` - Matrix lookup logic
- `server/plugins/mongoose.ts` - Change stream watcher
- `server/plugins/scheduler.ts` - Daily expiration job
- `server/models/Deal.ts` - Mongoose schema (hyper_front_status: String)
- `server/models/Matrix.ts` - Mongoose schema for matrix collection
- `scripts/data/matrix.csv` - Source CSV for matrix data
- `scripts/insertMatrixData.cjs` - Seed script
- `.workflow/tests/createAnonymousDeal.cjs` - Test script for deal creation
- `.workflow/tests/checkHyperFrontStatus.cjs` - Test script for status verification

## Related Knowledge
- [[MMH-1373]] - Modify button fix and Cancelled→Canceled cleanup
- [[use-deal-status]] - Frontend composable for status checks
