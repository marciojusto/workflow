# Hyperfront

**Vision:** Web application for Miles Mobility Platform — manage vehicle leasing deals, proposals, and contract lifecycle.
**For:** Dealers, fleet managers, and internal ops teams at Mobilize Financial Services.
**Solves:** End-to-end deal management from quotation to contract delivery, with integrated credit assessment, stipulations, and document generation.

## Goals

- Provide complete deal lifecycle UI (quote → proposal → contract → delivery)
- Integrate with 10+ MMP APIs (Miles/Sofico Platform)
- Minimise manual data entry through smart defaults and pre-fill
- Enable role-based access with Okta SSO

## Tech Stack

**Core:**
- Framework: Nuxt 3 + Vue 3 (Composition API)
- Language: TypeScript (strict: false)
- UI: Quasar Framework
- State: Pinia with persisted state
- Styling: SCSS with BEM-like naming

**Key dependencies:**
- `@mfs/mmp-ui-kit` — Internal component library
- `bsClient` — Custom API client for deal-bs backend
- `consola` — Logging
- `vitest` — Test runner

## Scope

**v1 includes:**
- Deal CRUD with status workflow (active/cancelled/pending)
- Party management (customer, driver, fleet data)
- Proposal generation with secci flow
- Stipulations/terms management
- Document template management
- Vehicle catalog browsing
- Contract management and delivery scheduling
- Dashboard with deal list and filtering

**Explicitly out of scope:**
- Mobile app (responsive web only)
- Offline mode
- Real-time notifications (polling-based)
- Multi-language beyond FR/EN

## Constraints

- **Timeline:** Ongoing delivery with Jira ticket-based workflow
- **Technical:** All API calls must use `bsClient` pattern (SoC via server/api/ endpoints)
- **Resources:** Single frontend developer + backend team
