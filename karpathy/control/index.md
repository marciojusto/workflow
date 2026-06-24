# Wiki Index - Karpathy Method

## Directories Overview

- **raw/files/**: Original documents (PDFs, captures, repos) - MMH_1435 project files
- **raw/openapi/**: OpenAPI specifications (MMP APIs)
- **wiki/**: Generated markdown notes
  - `references/`: References and sources
- **history/**: Migrated historical files
- **control/**: Governance files (this index, log)

## Last Updated
2026-06-05

## Wiki Contents

### Concepts
- **use-deal-status.md**: Composable for deal status computations with case-insensitive matching and spelling normalization (Canceled/Cancelled)
- **hyper-front-status.md**: Complete documentation of the hyper_front_status system, matrix collection, data flow, and common issues

### Projects (Tickets)
- **MMH-1357.md**: Duplicate deal / reopen deal flow fixes — 2 bugs cataloged (party.zipCode not assigned, offerStore undeclared) + 5 related fixes (backend 422, customerId injection, merge logic, PayloadBuilder hash)
- **MMH-1373.md**: Fix for modify button accessibility on terminal status deals (canceled, rejected, expired) + hyper_front_status deep investigation
- **MMH-1494.md**: Fallback mock PDF in printQuote when template not found — base64 PDF in JSON response, removed separate GET endpoint
- **MMH-1496.md**: Customer data missing in deal list after save — Miles disabled enumGroupId, fixed entity inference and 4 bypass paths in partyMapper.ts + dealPayloadBuilder.ts
- **MMH-1516.md**: CLONE — User Hyperfront as a Seller (Seller RBAC) — deal filtering by `x-seller-id`, reattribute gating, commission visibility, middleware auth infrastructure
- **MMH-1544.md**: Company & Seller Filter Missing in BFF Endpoints — `buildAccessFilter()` utility, 3 BFF endpoints fixed, DRY refactor of deals.get and deal-list.get

### Conversations
- **deal-submission-and-reassignment.md**: Deal submission and reassignment process review (29/Jan/2026) - Marcio & Rania discussion on deal lifecycle, reassignment limitations, and Sofico ticket
- **Clarifying_Broker_Terminology_and_Addressing_API_Deployment_Challenges.md**: Broker terminology clarification (broker=dealership vs broker contact=salesperson) + API deployment bottlenecks and technical issues (14/May/2026) - Marcio & Hendrik

### References
- health-check.md
- mmp-apis.md
- test.md
- release-notes-1.5.7.md - Hyperfront Release Notes v1.5.7

## Status
Wiki populated with concept and project notes. Ready for knowledge queries.