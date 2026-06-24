# Wiki Log - Karpathy Method

## 2026-04-29 - Initial Setup
- Directory structure created at `.workflow/karpathy/`
- Migrated files from `.workflow/RAG/` and `.workflow/history/`
- Created initial index.md manually
- **Issue**: wiki-keeper agent times out (10min) without producing output - needs investigation

## 2026-05-02 - Bug Fix MMH-1373
- **Ticket**: MMH-1373 - Modify button accessibility for canceled deals
- **Issue**: Modify button incorrectly visible for terminal status deals (canceled, rejected, expired)
- **Root Cause**: Case-sensitive status comparisons and missing expired status check
- **Fix Applied**:
  - Normalized status comparisons to be case-insensitive
  - Added support for both "Canceled" and "Cancelled" spellings
  - Added isExpired check to modify button logic in Offer.vue and FinancingActions.vue
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1373.md` - Ticket implementation note
  - Created `wiki/concepts/use-deal-status.md` - Composable documentation
  - Updated `control/index.md` with new wiki contents
  - Updated `control/log.md` with this entry
- **Testing Results**: 44 tests passed, all acceptance criteria met
- **Status**: Implemented and tested

## Previous Notes
- RAG system was previously at `.workflow/RAG/`
- Historical files migrated to `.workflow/karpathy/history/`

## 2026-05-05 - hyper_front_status Deep Investigation & "Cancelled"→"Canceled" Fix
- **Ticket**: MMH-1373 - Additional investigation
- **Context**: User reported Offer Status still showing "Cancelled" despite code fixes
- **Root Cause**: Two issues found:
  1. Matrix CSV was fixed but `insertMatrixData.cjs` seed script was never re-run → MongoDB `matrix` collection still had 10 rows with "Cancelled"
  2. Existing deals persisted with "Cancelled" in their `hyper_front_status` field
- **Fixes Applied**:
  - `scripts/data/matrix.csv`: All "Cancelled" → "Canceled" in hyper_front_status column
  - Re-ran `node scripts/insertMatrixData.cjs` to seed MongoDB
  - Direct MongoDB update: 1 deal updated from "Cancelled" → "Canceled"
- **Wiki Updates**:
  - Updated `wiki/projects/MMH-1373.md` - Added complete hyper_front_status investigation section
  - Created `wiki/concepts/hyper-front-status.md` - New comprehensive concept note
  - Updated `control/index.md`
  - Updated `control/log.md`
- **Validation**: E2E test via validator agent confirmed anonymous deal creation correctly populates hyper_front_status via change stream

## 2026-05-12 - Bug Fix MMH-1357 (Duplicate Deal / Reopen Deal Flow)
- **Ticket**: MMH-1357 - Duplicate deal and reopen deal flow fixes
- **Bug 1 (MMH-1357-BUG-001)**: `party.zipCode` never assigned after zipCode API search in `partiesModule.ts` — caused "Please complete required fields" error blocking Next button
- **Bug 2 (MMH-1357-BUG-002)**: `offerStore` used without declaration in `validateCommunicationField` (`shared/utils/index.ts`) — caused ReferenceError blocking step navigation
- **Related Fixes (5)**: Backend `ignore_warnings` param, customerId injection, merge logic in `infos.get.ts`, PayloadBuilder null fix, duplicate response customerId override
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1357.md` — Full bug catalog with root causes, fixes, and file references
  - Updated `control/index.md` with new project entry
  - Updated `control/log.md` with this entry
- **Status**: Implemented and tested

## 2026-05-11 - Release Notes v1.5.7 Ingestion
- **Source**: `raw/files/release notes/Hyperfront_Release_Notes_version_1.5.7.xlsx`
- **File Type**: Excel (.xlsx)
- **Contents**: 38 items (9 Stories, 22 Bugs, 7 Internal Tasks)
- **Wiki Updates**:
  - Created `wiki/references/release-notes-1.5.7.md` - Full release notes with all entries organized by type
  - Updated `control/index.md` with new reference entry
  - Updated `control/log.md` with this entry

## 2026-05-14 - Conversation Ingestion: Deal Submission & Reassignment
- **Source**: `wiki/conversations/deal-submission-and-reassignment.md` (converted from .txt)
- **Conversation**: Marcio & Rania — Deal submission and reassignment process review (29/Jan/2026)
- **Key Topics**: Deal lifecycle (document upload → contract activation), reassignment only in simulation phase, Sofico ticket for extension to other phases
- **Tags**: #conversa #offer #contract #delivery #hyperfront
- **Wiki Updates**:
  - Registered `wiki/conversations/` directory in control/index.md
  - Updated `control/log.md` with this entry
  - Synced with Obsidian vault
- **Status**: Ingested and indexed

## 2026-05-14 - Conversation Ingestion: Broker Terminology & API Deployment
- **Source**: `wiki/conversations/Clarifying_Broker_Terminology_and_Addressing_API_Deployment_Challenges.md` (converted from .txt)
- **Conversation**: Marcio & Hendrik — Broker terminology (broker=dealership, broker contact=salesperson) + API deployment bottlenecks and technical issues in deal-bs/hyperfront
- **Key Topics**: MMP vs Miles broker terminology, dealership manager reattribute rules, API gateway deployment bottlenecks (Usama), logging issues in deal-bs, Pinia DevTools missing, Logbook filter not merged
- **Tags**: #conversa #party #deal-bs
- **Wiki Updates**:
  - Registered conversation note in `wiki/conversations/`
  - Updated `control/index.md` with new conversation entry
  - Updated `control/log.md` with this entry
  - Synced with Obsidian vault
- **Status**: Ingested and indexed

## Next Steps
- Investigate wiki-keeper agent timeout
- Test health check with a simple query
- Verify workflow-orchestrator delegation to wiki-keeper
- Cleaned up duplicate folders: removed Spanish conceptos/, referencias/, projetos/ - kept only English references/

## 2026-05-22 - MMH-1494: Implement Fallback Mock PDF in printQuote
- **Ticket**: MMH-1494 - Implement fallback mock PDF in printQuote when template not found
- **Issue**: When no matching document template was found, backend threw IllegalArgumentException — frontend had a separate GET `/mock-pdf` endpoint to fetch a fallback PDF
- **Fix Applied**:
  - Modified `TemplateServiceImpl.printQuote()` to return JSON with `createdPdf.binary` (base64) in both success and fallback paths
  - Fallback loads `mock.pdf` from classpath as base64 on missing template
  - Removed GET `/mock-pdf` endpoint from TemplateController
  - Frontend: replaced `/mock-pdf` URL fetch with base64→blob URL→printPdf() in Offer.vue, Third.vue, FinancingActions.vue
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1494.md` - Ticket implementation note
  - Updated `control/index.md` with new project entry
  - Updated `control/log.md` with this entry
- **Testing Results**: 17 tests pass (10 printQuote + 7 others)
- **Status**: Implemented

## 2026-05-26 - Bug Fix MMH-1496
- **Ticket**: MMH-1496 - Customer Data Missing in Deal List After Save (Visible in Miles)
- **Root Cause**: Miles backend disabled `enumGroupId` return — `resolveEntityGroupId()` returned null and 4 bypass paths read `customerObj?.legalEntity?.enumGroupId` directly
- **Fix Applied**:
  - Added fallback entity inference in `resolveEntityGroupId()` (infers from individualPerson/tradingName/vatNumber presence)
  - Fixed 4 bypass paths in `buildProposalIndOrST`, `buildProposalOrg`, `buildProposalParty`, `mapPartyDetailsSimulation`
  - Added null guard in `dealPayloadBuilder.ts` for `getLabelClientType()`
- **Files Changed**: `partyMapper.ts` (6 changes), `dealPayloadBuilder.ts` (1 change)
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1496.md` — Ticket implementation note with full root cause, fix catalog, and validation results
  - Updated `control/index.md` with new project entry
  - Updated `control/log.md` with this entry
- **Testing Results**: 64/67 tests pass (3 pre-existing zipcode failures unrelated)
- **Status**: Implemented and tested

## 2026-06-05 - Seller RBAC Implementation (MMH-1516)
- **Ticket**: MMH-1516 — CLONE - User Hyperfront as a Seller
- **AC01**: Deal filtering by owner via `x-seller-id` header + manager bypass
- **AC03**: Navigation menu & offer access — `Roles.SELLER` added to offer/edit
- **AC04**: Cannot reattribute deals — `hiddenActions` prop + `canReattribute` gate
- **AC06**: Commission visibility — `canSeeCommissions` gate in OfferDetails.vue
- **Cross-cutting**: Middleware `matchRoute()` parameterized paths, 3-tier `getAccessToken()` fallback, `BFF_ROUTE_ROLES` extended
- **Testing**: 86/87 tests pass (1 pre-existing timeout), new 29-test regression suite `MMH-1516-rbac-full-flow.spec.ts`, browser E2E validated with `ds40153`
- **Cleanup**: Removed `auth/api.ts`, `requests/useApi.ts`, `plugins/axios.client.ts`, axios from noExternal
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1516.md` — Full implementation note
  - Updated `control/index.md` with new project entry
  - Updated `control/log.md` with this entry
- **Status**: Implemented and tested

## 2026-06-12 — MMH-1544: Company & Seller Filter Missing in BFF Endpoints
- **Ticket**: MMH-1544 — Company & Seller Filter Missing in BFF Endpoints
- **Problem**: `x-brokers` (company filter) and `x-seller-id` (seller filter) headers were missing in 3 BFF endpoints
- **Fix Applied**:
  - Created `server/utils/accessControl.ts` with `buildAccessFilter(event)` shared utility
  - Refactored `deals.get.ts` and `deal-list.get.tsx` to use shared utility
  - Fixed `deals/[id].get.ts`, `dashboard/stats.get.ts`, `deals/pick-list.post.ts` — added missing filters
- **Wiki Updates**:
  - Created `wiki/projects/MMH-1544.md` — Ticket implementation note
  - Updated `control/index.md` with new project entry
  - Updated `control/log.md` with this entry
  - Synced with Obsidian vault
- **Testing**: All 14 existing tests pass, coherence checker approved
- **Status**: Implemented and tested

## 2026-04-30 - Health Check
- **OpenAPI specs**: 10 files present (miles-car-quote, miles-catalog, miles-contract, miles-credit-retail, miles-customer, miles-dealer-pos, miles-document, miles-driver, miles-quotation, miles-supplier)
- **MMH_1435**: 1 file (Asset Tab V1.xlsx)
- **Wiki structure**: Only `wiki/references/` exists with 3 files (health-check.md, mmp-apis.md, test.md)
- **Observation**: `wiki/concepts/` and `wiki/projects/` directories are missing - may need to be created as knowledge grows
- **Status**: Wiki is sparse - only reference notes exist, no concept or project notes yet