# MMH-1406 - Fix Duplicated Third Party Types in "Add Third Party" Menu

## Bug Description
During the Proposal phase, the "Add Third Party" dropdown shows "Guarantor" and "Co-borrower" each listed twice. This is caused by duplicate documents in the MongoDB `enumerationdatas` collection for enum ID 720 (CoCustomerType).

## Approach: Hybrid (Immediate Fix + Permanent Prevention)

### Phase 1: Immediate Fix (Low Risk)
Deduplicate the API response at the `pick-list.post.ts` endpoint to eliminate duplicates from the dropdown **without** modifying the database.

### Phase 2: Permanent Prevention
Add a unique compound index to the `EnumerationData` model and provide a migration script to clean up existing duplicates.

---

## Phase 1: Immediate Fix — API-Level Deduplication

### File: `server/api/enums/pick-list.post.ts`

**Current behavior (lines 89-99):** The `reduce()` pushes ALL matching MongoDB documents into `acc[key]` without checking for duplicates — if MongoDB has 2 rows with `enumeration_value = "Guarantor"` for enum ID 720, the API returns both.

**Fix:** Add deduplication by using a `Set` keyed on `enum_id` (which represents the unique value ID) before pushing into the array:

```typescript
const localPicklist = localEnumData.reduce((acc, item) => {
  const key = item.id;
  if (!acc[key]) acc[key] = [];
  
  // Deduplicate by enum_id to prevent duplicates from DB
  const isDuplicate = acc[key].some(
    (existing: any) => existing.value === item.enum_id
  );
  if (!isDuplicate) {
    acc[key].push({
      value: item.enum_id,
      label: item.enumeration_value,
      group: item.group_enumeration_value,
    });
  }
  return acc;
}, {} as Record<string, any[]>);
```

**Why this is safe:**
- `enum_id` is the unique identifier for the picklist value
- If two DB records have the same `enum_id`, they represent the same option
- This does NOT mask bugs for other fields since it only affects the response shape
- No database changes required

---

## Phase 2: Permanent Fix — Unique Index + Cleanup

### File: `server/models/EnumerationData.ts`

Add a unique compound index to prevent future duplicates at the database level:

```typescript
EnumerationDataSchema.index(
  { id: 1, enum_id: 1 },
  { unique: true, background: true }
);
```

### New Script: `scripts/cleanupEnumDuplicates.cjs`

Create a one-time cleanup script that:
1. Queries all duplicate `(id, enum_id)` pairs in `enumerationdatas`
2. Removes duplicate entries, keeping only the first occurrence
3. Reports how many duplicates were found and removed per enum ID
4. Has a `--dry-run` flag for safe preview

**Dry-run mode:**
```bash
node scripts/cleanupEnumDuplicates.cjs --dry-run
# Output: Found 2 duplicates for enum 720 (CoCustomerType)
```

**Execute cleanup:**
```bash
node scripts/cleanupEnumDuplicates.cjs
```

---

## Implementation Steps

| Step | File | Description | Risk |
|------|------|-------------|------|
| 1 | `server/api/enums/pick-list.post.ts` | Add deduplication by `enum_id` in the `reduce()` function | LOW |
| 2 | `server/models/EnumerationData.ts` | Add unique compound index `{ id: 1, enum_id: 1 }` | LOW (background index) |
| 3 | `scripts/cleanupEnumDuplicates.cjs` | Create cleanup script with dry-run support | LOW |
| 4 | Run cleanup on REF DEV → REF ASY → PROD | Execute cleanup per environment | MEDIUM |

---

## RAG Materials Used
- None — no RAG materials were provided for this ticket

## RAG Materials NOT Used
- N/A

## References
- `server/api/enums/pick-list.post.ts` — API endpoint where deduplication will be applied
- `server/models/EnumerationData.ts` — Model where unique index will be added
- `scripts/data/enumerationsData.csv` — Seed data (confirmed clean — single entries per type)
- `features/deal/Offer.vue` — UI component with the "Add Third Party" dropdown
- `features/hyperFront/components/SelectComponent.vue` — Generic select component (no changes needed)
- `shared/config/layout/dealPageConfig.ts` — Field config for thirdRole with `enumId: "720"`

## Validation Checklist
- [ ] Dropdown shows exactly 2 options: "Guarantor" and "Co-borrower" (no duplicates)
- [ ] Selecting "Guarantor" creates a party with `role_code = "guarantor"` and correct `co_customer_type`
- [ ] Selecting "Co-borrower" creates a party with `role_code = "coborrower"` and correct `co_customer_type`
- [ ] Cleanup script dry-run correctly identifies duplicates without modifying data
- [ ] Cleanup script execution removes duplicates and reports count
- [ ] Other enum IDs in the system are NOT affected by the change
- [ ] ESLint passes (`npm run lint`)
