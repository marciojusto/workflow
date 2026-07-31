# Plan: MMH-1465 — Party fields Remain Editable After Saving in Proposal Phase

## AC
Fix the bug described in the ticket description:
1. Save button should disable all fields.
2. To edit, click "Modify" button
3. Save button should lock all fields again.

## Problem Analysis

During the Proposal phase, after completing all Party fields and clicking the Save button:
- Data is correctly saved.
- Fields **remain editable** instead of becoming greyed out and read-only.

### Root Cause

In `features/party/Third.vue`, the `updatePartyReadonlyFields()` function only makes **some** fields readonly after saving in Proposal phase:
- **Client parties**: only `partyType`, `birthDate`, `zipCode`, `fiscalCode`, `companyFiscalCode` become readonly. All other fields remain editable.
- **Non-client parties** (with `applicantCreditScoreId`): only `partyType`, `fiscalCode`, `companyFiscalCode` become readonly. All other fields remain editable.

Additionally, for **client parties** saved via `Offer.vue`'s global Save button, `updatePartyReadonlyFields()` is never called after save.

The user confirmed that a **"Modify" button already exists** at the Party tab level (in `Offer.vue`), so no new button is needed.

## Solution Overview

Introduce a per-party `lockedPartyIndices` state in the offer store to track which parties have been saved and locked in the Proposal phase. Use this state to make ALL fields readonly. The existing "Modify" button will unlock all parties for editing.

## Files to Change

1. `features/offers/stores/offer.ts`
2. `features/party/Third.vue`
3. `features/deal/Offer.vue`

## Implementation Steps

### Step 1: Add `lockedPartyIndices` to offer store (`features/offers/stores/offer.ts`)

- Add `lockedPartyIndices: number[]` to `OfferState` interface.
- Initialize `lockedPartyIndices: []` in the store state.
- Add action `lockParty(index: number)` that pushes the index into `lockedPartyIndices` (avoid duplicates).
- Add action `unlockParty(index: number)` that filters the index out of `lockedPartyIndices`.

### Step 2: Update `Third.vue` to use `lockedPartyIndices`

- Add computed `isPartyLocked` that checks if `props.partyIndex` is in `offerStore.lockedPartyIndices`.
- Modify `updatePartyReadonlyFields()`:
  - At the beginning of the function (after the `props.isActive` check), add:
    ```ts
    if (isPartyLocked.value && workflow.value === OfferWorkflow.PROPOSAL && !offerStore.partyTabUnlocked) {
      _setPageSections(applyFlatReadonly(pageConfig.value.sections, true));
      return;
    }
    ```
  - This makes **all** fields readonly when the party is locked in Proposal phase.
- In `saveUpdates()`, after successful save:
  ```ts
  if (workflow.value === OfferWorkflow.PROPOSAL) {
    offerStore.lockParty(props.partyIndex);
  }
  ```
- In `onMounted` and `onActivated`, if in Proposal and party has been saved (`applicantCreditScoreId` or `customerId`), lock the party:
  ```ts
  if (workflow.value === OfferWorkflow.PROPOSAL && (party.value?.applicantCreditScoreId || party.value?.customerId)) {
    offerStore.lockParty(props.partyIndex);
  }
  ```
- Add a watch for `isPartyLocked` to call `updatePartyReadonlyFields()`.

### Step 3: Update `Offer.vue` to lock client parties after global save and unlock on Modify

- In `handleSaveAction()`, after `await Promise.all(promises)`:
  - If `offerStore.workflow === OfferWorkflow.PROPOSAL`, iterate over `dirtyIndices` and call `offerStore.lockParty(idx)` for each.
- In `handleUnlockPartyTab()`:
  - After `offerStore.setPartyTabUnlocked(true)`, unlock all parties:
    ```ts
    for (let i = 0; i < partiesStore.parties.length; i++) {
      offerStore.unlockParty(i);
    }
    ```

## Validation

- After saving a party in Proposal phase, all input fields in that party tab should be greyed out / readonly.
- Clicking the existing "Modify" button should re-enable all fields.
- Clicking "Save" again should re-lock all fields.
- Existing behavior in Simulation workflow should be unaffected.
- Existing MFS Request / Under Study behavior should be unaffected.
