# Project Structure

**Root:** `~/Development/teamwill/mobilize/hyperfront`

## Directory Tree (key dirs)

```
hyperfront/
├── features/          # Feature-based modules (auth, dashboard, dealers, offers)
│   ├── auth/          # Okta login, permissions
│   ├── dashboard/     # Deal dashboard + lists
│   ├── dealers/       # Dealer management
│   └── offers/        # Offer/proposal views
├── pages/             # Nuxt page routes
├── layouts/           # Page layouts
├── server/
│   ├── api/           # API endpoints (REST)
│   ├── services/      # bsClient API client
│   └── utils/         # bsFetch utility
├── shared/
│   ├── components/    # Reusable Vue components
│   ├── stores/        # Shared Pinia stores
│   ├── styles/        # Global SCSS
│   └── utils/         # Utility functions
├── plugins/           # Nuxt plugins
├── tests/             # Test files
├── playwright/        # E2E tests + page objects
└── scripts/           # MongoDB scripts, CSV data
```

## Module Organization

### Deals Module

**Purpose:** Core deal CRUD, status management, tabs (party, financing, stipulations, etc.)
**Location:** `features/offers/`, `pages/deal/`
**Key files:** Deal detail page, deal creation flow, status management composables

### Dashboard

**Purpose:** Deal listing, filtering, search
**Location:** `features/dashboard/`, `pages/index.vue`
**Key files:** Dashboard list components, filter composables

### Auth

**Purpose:** Okta SSO integration, role-based access
**Location:** `features/auth/`
**Key files:** Login page, auth store, permission guards
