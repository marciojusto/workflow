# "Clarifying UI Behavior for Proposal Phase" summary

**Date:** Apr 23, 2026  
**Time:** 14:34 – 14:45 GMT+1:00

---

## Summary

The team clarified the complex UI behavior of save and modify buttons in the proposal phase to resolve a critical bug.

### Key Points

#### Initial Bug Discussion

The meeting began with a discussion about a specific bug related to field graying out.

* The bug involves fields not graying out as expected after saving data in the proposal phase.
* The expected behavior is for all fields to become grayed out upon saving.

#### Expected Field Behavior

Participants clarified the precise sequence of field states during the proposal process.

* Initially, fields are enabled for data entry, especially for anonymous clients.
* Upon clicking 'save', all fields should become disabled (grayed out).
* Clicking 'modify' re-enables all fields for editing.
* Saving again after modification should disable all fields once more.

#### Complex 'Modify' Logic

The discussion delved into the nuanced functionality of the 'modify' button.

* The first click on 'modify' enables fields without changing the offer status if all fields were previously grayed out.
* A second click on 'modify' changes the offer status and redirects to the simulation phase, allowing changes to fields like birth date or postal code.
* If not all fields are grayed out and 'modify' is clicked, the user is immediately redirected to the simulation phase.

#### Simulation Phase Interaction

The interaction between the proposal and simulation phases was detailed.

* Fields not filled during the anonymous simulation phase remain enabled in the pending proposal phase.
* Changes to birth date or postal code are only possible in the simulation phase.