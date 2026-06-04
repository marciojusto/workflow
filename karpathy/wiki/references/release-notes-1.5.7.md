# Hyperfront Release Notes - Version 1.5.7
- **Original Source**: `raw/files/release notes/Hyperfront_Release_Notes_version_1.5.7.xlsx`
- **Processing Date**: 2026-05-11
- **Tags**: #release-notes #hyperfront #v1.5.7
---

## Overview

Release **1.5.7** includes **38 items**: 9 Stories, 22 Bugs, and 7 Internal Tasks. Key themes include OKTA integration, document screen UX, deal lifecycle management, and simulation fixes.

---

## Stories (9)

| Key | Description | Jira |
|-----|-------------|------|
| MPP-357 | Connection to OKTA to REF DEV (Part 1 - With single role) | MFSMP-4236 |
| — | UX review of document screen | MFSMP-19097 |
| — | Deal list - Access expired deals | MFSMP-18015 |
| — | Inputs limitation rules | MFSMP-19446 |
| — | Manage fees - Financial product | MFSMP-13241 |
| — | Cancel the deal in "under study" status | MFSMP-14564 |
| MPP-3925 | Search for existing client / Create client in RDV (integration with RDV) | MFSMP-12352 |
| — | [MFS request] - Manage statuses | MFSMP-4157 |
| — | Manage rejected deal | MFSMP-4156 |

## Bugs (22)

| Description | Jira |
|-------------|------|
| Pop-up "share data privacy" is not appearing | MFSMP-18853 |
| Documents screen - Visual feedback after document upload should be changed | MFSMP-17631 |
| Error during simulation | MFSMP-23210 |
| Documents screen - Issue uploading co-actor documents | MFSMP-23210 |
| Simulation screen - User should be able to save even if all data are not filled in (proposal phase) | MFSMP-21175 |
| Documents screen - Issue uploading co-actor documents | MFSMP-19693 |
| For sole trader, VAT number is required while not marked as mandatory | MFSMP-18683 |
| Documents screen - Error when saving data (sole trader client - proposal phase) | MFSMP-18203 |
| Asset screen - Check VAT number format during input | MFSMP-18199 |
| Documents screen - Visual feedback after document upload should be changed | MFSMP-17631 |
| Quotation: Format of trade in and downpayment missing | MFSMP-17593 |
| For new customers, BankAccount state and type is wrongly set in miles to "100002" | TW internal |
| Document Status Not Updated in Miles After Deletion in HyperFront | TW internal |
| Party fields Remain Editable After Saving in Proposal Phase | TW internal |
| Failed to add guarantor | TW internal |
| Call to marketing-preferences returns 404 | TW internal |
| The cron job that changes the status from "Under Study" to "Delivery" is not working. | TW internal |
| sole trader and company: create deal fails with error "required fields missing" | TW internal |
| Driver Phone Number should be Synced with Client for Non-Anonymous Individual type | TW internal |
| Navigation Blocked in Proposal Phase Due to Disabled "Send by Email" Button in Data Privacy Popup | TW internal |
| print button is disabled when based on rules management | TW internal |
| Upload document is not working with error "no Route" | TW internal |
| Sim phase - Cannot enter 10.000 EUR for Residual Value | TW internal |
| Missing Miles Configuration Blocking "Extract Document Stipulations" Display in Hyperfront (MPP-272) | TW internal |
| Simulation phase - When deleting one other simulation, the proposal cannot be submitted due to business validation errors because the quote has status "web canceled" in miles | TW internal |
| Cron Job Design and Permission Issues Affecting Deal List Performance | TW internal |

## Internal Tasks (7)

| Description | Area |
|-------------|------|
| Error mgmt - Live error log screen displaying latest error messages | Error Management |
| Theft&Fire config fixing | Configuration |
| Delete unused files and code [enhancement] | Code Cleanup |

*Note: 7 internal tasks listed above share "TW internal" as Jira reference.*

## Themes & Areas Affected

- **OKTA / Auth**: MPP-357 connection to OKTA with single role
- **Documents**: UX review, upload feedback, co-actor upload, sole trader saving issues (multiple bugs)
- **Deal Lifecycle**: Cancel under study, manage rejected deals, access expired deals, manage statuses
- **Simulation**: Error during sim, save incomplete data, residual value input, quote "web canceled" status
- **Integration (RDV)**: Search/create client with RDV (MPP-3925)
- **Client Data**: VAT validation, bank account state/type, party field editability, driver phone sync
- **Configuration**: Theft&Fire config, rules management, missing Miles config blocking stipulations
- **Internal Quality**: Error logging, unused code removal, cron job fixes, performance

## Related Wiki Notes
- [[MMH-1373]] - Deal status handling (canceled/cancelled normalization)
- [[hyper-front-status]] - Hyperfront status system and matrix collection
- [[use-deal-status]] - Deal status composable