# Implementation Plan: MMH-1358 AC01 - Centralized Deal Status

## Overview
Implement centralized deal status checking via composable and update OfferActionsBar.vue to comply with AC01 requirements.

## Phase 1: Create useDealStatus Composable
**File:** `composables/useDealStatus.ts`

Create a new composable that centralizes all deal status checks:
- Arrow function pattern (per AGENTS.md)
- Individual status checks: isUnderStudy, isRejected, isCancelled, isExpired, isMfsRequest
- Combined checks: canCancel (for AC01), isReadOnly
- Uses offerStore for reactive status tracking

## Phase 2: Add EXPIRED_STATUS Constant
**File:** `shared/constants.ts` (line 7)

Add: `export const EXPIRED_STATUS = "Expired"`

## Phase 3: Refactor OfferActionsBar.vue

### Replace Lines 141-149
Replace individual computed properties with composable:
```typescript
const { 
  isUnderStudy, 
  isRejected, 
  isCancelled, 
  isExpired, 
  isMfsRequest, 
  canCancel 
} = useDealStatus()
```

### Update Line 6 (Cancel Button Visibility)
From:
```
v-if="showCancelButton && !isRejectedStatus && !iUpdateRequest"
```
To:
```
v-if="showCancelButton && canCancel"
```

### Remove Line 11 (Cancel Button Disabled State)
Remove `:disabled="isUnderStudyStatus"` - AC01 requires button to be ENABLED in Under Study status.

### Update References Throughout File
Replace all usages of old computed properties:
- `isRejectedStatus` → `isRejected` (lines 39, 58, 237, 281, 290)
- `isCancelledStatus` → `isCancelled` (lines 39)
- `isUnderStudyStatus` → `isUnderStudy` (lines 58, 66, 74, 85)
- `iUpdateRequest` → `isMfsRequest` (line 180)

## AC01 Compliance Verification

| Status | Before | After |
|--------|--------|-------|
| Under Study | Disabled ❌ | Enabled ✅ |
| Expired | Not checked ❌ | Hidden ✅ |
| Rejected | Hidden ✅ | Hidden ✅ |
| Cancelled | Hidden ✅ | Hidden ✅ |

## Testing Checklist
- [ ] Cancel button visible in Under Study status
- [ ] Cancel button hidden in Rejected status  
- [ ] Cancel button hidden in Cancelled status
- [ ] Cancel button hidden in Expired status
- [ ] No console errors
- [ ] Lint passes
