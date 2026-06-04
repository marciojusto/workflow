# useDealStatus Composable
- **Original Source**: composables/useDealStatus.ts
- **Processing Date**: 2026-05-02
- **Tags**: #composable #deal-status #vue #typescript
---

## Overview
The `useDealStatus` composable provides reactive computed properties for determining deal state and terminal status. It is used across the application to control UI visibility and business logic based on deal status.

## Purpose
Centralize deal status logic to ensure consistent behavior across all components that need to check deal states. This composable handles:
- Case-insensitive status comparisons
- Spelling variations (e.g., "Canceled" vs "Cancelled")
- Reactive status updates from the deal object

## API

### Computed Properties

#### `isTerminal`
Returns `true` if the deal is in any terminal state (canceled, rejected, expired).

#### `isRejected`
Returns `true` if the deal status indicates rejection.
- **Implementation**: Case-insensitive comparison with REJECTED_STATUS
- **Handles**: "Rejected", "REJECTED", "rejected", etc.

#### `isCancelled`
Returns `true` if the deal status indicates cancellation.
- **Implementation**: Case-insensitive comparison with both "Cancelled" and "Canceled" spellings
- **Handles**: 
  - British spelling: "Cancelled", "CANCELLED", "cancelled"
  - American spelling: "Canceled", "CANCELED", "canceled"

#### `isExpired`
Returns `true` if the deal status indicates expiration.
- **Implementation**: Case-insensitive comparison with EXPIRED_STATUS
- **Handles**: "Expired", "EXPIRED", "expired", etc.

## Usage Pattern

```typescript
import { useDealStatus } from '@/composables/useDealStatus'

// In component setup
const { isTerminal, isRejected, isCancelled, isExpired } = useDealStatus()

// Use in template
<div v-if="isCancelled">This deal is cancelled</div>
<div v-if="!isTerminal">Show modify button</div>

// Use in computed properties
const showModifyButton = computed(() => {
  return !isCancelled.value && !isRejected.value && !isExpired.value
})
```

## Status Comparison Logic

### Before Fix (Buggy)
```typescript
isCancelled: computed(() => status.value === CANCELLED_STATUS)
isRejected: computed(() => status.value === REJECTED_STATUS)
isExpired: computed(() => status.value === EXPIRED_STATUS)
```

**Problems**:
- Exact string match only worked for one casing
- "Canceled" (American) not matched when backend returned "Cancelled" (British)

### After Fix (Correct)
```typescript
isRejected: computed(() => 
  status.value?.toLowerCase() === REJECTED_STATUS.toLowerCase()
),
isCancelled: computed(() => {
  const normalizedStatus = status.value?.toLowerCase()
  return normalizedStatus === CANCELLED_STATUS.toLowerCase() || 
         normalizedStatus === 'canceled'.toLowerCase()
}),
isExpired: computed(() => 
  status.value?.toLowerCase() === EXPIRED_STATUS.toLowerCase()
)
```

**Benefits**:
- Case-insensitive matching
- Handles both "Canceled" and "Cancelled" spellings
- Robust against backend casing variations

## Affected Components

### Direct Users
- `features/deal/Offer.vue` - Controls modify button visibility
- `features/financing/components/FinancingActions.vue` - Controls financing modify button
- Any component checking deal terminal status

### Status-Based UI Controls
The composable is used to:
- Show/hide modify buttons
- Enable/disable action buttons
- Display appropriate warnings for terminal deals
- Control form editability

## Terminal Deal States

A deal is considered terminal when in any of these states:
1. **Canceled/Cancelled** - Deal was cancelled by user or system
2. **Rejected** - Deal was rejected during approval process
3. **Expired** - Deal exceeded its validity period
4. **DRAFT** - Deal is still being prepared
5. **PENDING_DOCUMENTS** - Awaiting required documentation
6. **PENDING_APPROVAL** - Awaiting approval decision

## Related Concepts
- [[Deal Status Flow]] - Business logic for deal lifecycle transitions
- [[MMH-1373]] - Bug fix ticket for modify button accessibility

## Implementation Notes

### Null Safety
All computed properties use optional chaining (`?.`) to handle cases where `status.value` might be undefined.

### Reactive Updates
The composable automatically reacts to status changes from the parent deal object, ensuring UI stays in sync.

### Localization Considerations
The composable works with raw status strings from the backend. UI labels should use i18n translations if display is needed.

### Backend Data Source
Deal status values originate from MongoDB's `deal` collection, specifically the `hyper_front_status` field. This field is populated by backend services through:

1. **Scheduled Jobs** (`server/plugins/scheduler.ts`): Daily job that marks deals as "Expired" based on expiration dates
2. **Change Streams** (`server/plugins/mongoose.ts`): Real-time monitoring of deal collection for status updates
3. **Direct Updates**: Various business logic services that update deal status during workflow transitions

The frontend receives status values verbatim from API responses, which is why case-insensitive comparison is critical for robust behavior.

## Testing
- Unit tests verify correct status detection for all variations
- E2E tests confirm UI behavior matches expected states
- No regressions in status-based functionality

## Version History
- **2026-05-02**: Fixed case-sensitivity and spelling variations (MMH-1373)
- **Previous**: Initial implementation
