# External Integrations

## Authentication

**Service:** Okta SSO
**Purpose:** User authentication and role-based access
**Implementation:** `features/auth/` with Okta OIDC flow
**Configuration:** `OKTA_CLIENT_ID`, `OKTA_ISSUER`, `OKTA_REDIRECT_URI` in `.env`

## Backend API

**Service:** deal-bs (Java Spring Boot)
**Purpose:** All business logic for deal management, proposals, parties, contracts
**Implementation:** `server/services/bsClient.ts` — custom API client with retry support
**Authentication:** Okta JWT token (OktaJwtTokenProvider)
**Key endpoints:** Deals CRUD, party management, proposal workflow, stipulations, baremes

## MMP Platform APIs

**Service:** Miles Mobility Platform (10+ APIs)
**Purpose:** Vehicle catalog, quotation, credit assessment, contract management
**Implementation:** Via deal-bs (not called directly from frontend)
**APIs:** Quotation, Car Quote, Catalog, Dealer POS, Contract, Credit Retail, Customer, Document, Driver, Supplier
