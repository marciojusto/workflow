# Architecture

**Pattern:** Feature-based modular monolith (Nuxt 3 full-stack framework)

## High-Level Structure

```
Browser → Nuxt 3 SSR (server/) → bsClient → deal-bs (Java Backend) → MMP APIs
                                     ↕
                              MongoDB (local state, sessions)
```

## Identified Patterns

### SoC API Layer

**Location:** `server/api/` → `server/services/bsClient.ts`
**Purpose:** All backend communication goes through `server/api/` endpoints. Vue components never call backend directly.
**Implementation:** Each API endpoint is a separate file in `server/api/`. The `bsClient` service wraps all deal-bs API calls.

### Feature Modules

**Location:** `features/*/`
**Purpose:** Group related components, stores, and composables by domain.
**Implementation:** Each feature has its own directory with stores/ and components/. Shared code lives in `shared/`.

### Page Object Pattern (Testing)

**Location:** `playwright/tests/page-objects/`
**Purpose:** Encapsulate Playwright selectors and actions for maintainable E2E tests.
**Implementation:** `DealCreatePage`, `DealDetailPage`, `DashboardPage` with typed methods.

## Data Flow

### Deal Creation

```
User fills form → Nuxt composable → server/api/deals/create.post.ts → bsClient.deals.createDealBS() → deal-bs API
```

### Deal Status

```
Page load → Pinia store action → server/api/deals/[id].get.ts → bsClient → deal-bs → render deal detail view
```
