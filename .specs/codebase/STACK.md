# Tech Stack

**Analyzed:** 2026-05-19

## Core

- Framework: Nuxt 3 + Vue 3 (Composition API, `<script setup>`)
- Language: TypeScript (strict: false)
- Runtime: Node.js 20.19.5
- Package manager: npm

## Frontend

- UI Framework: Quasar 2.x
- Styling: SCSS (BEM-like naming), Quasar utility classes
- State Management: Pinia with `pinia-plugin-persistedstate`
- Form Handling: Quasar form components + composables

## Backend (deal-bs)

- Framework: Java Spring Boot
- API: REST/JSON via MMP platform
- DB: Oracle (behind deal-bs API)

## Testing

- Unit: Vitest
- E2E: Playwright (`playwright/` dir)
- Coverage: None configured

## External Services

- Auth: Okta SSO (OIDC)
- Platform: Miles Mobility Platform (10+ MMP APIs)
- Internal: `@mfs/mmp-ui-kit` component library

## Development Tools

- Linting: ESLint
- Container: Docker (SonarQube)
- Code Intelligence: GitNexus (knowledge graph)
