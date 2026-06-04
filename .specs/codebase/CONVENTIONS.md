# Code Conventions

## Naming Conventions

**Files:** PascalCase for components (`DealStatus.vue`), camelCase for utils (`useApi.ts`), RESTful API files (`[id].get.ts`)
**Functions/Methods:** camelCase (`createAnonymousDeal`, `navigateToTab`)
**Variables:** camelCase (`isLoading`, `dealId`)
**Constants:** SCREAMING_SNAKE_CASE (`API_BASE_URL`, `POSTAL_CODE`)

## Code Organization

**Imports:** External → internal (alias `@/`) → relative. Grouped by source.
**Component Structure:** `<template>` → `<script setup lang="ts">` → `<style scoped lang="scss">`

## Type Safety

- TypeScript with `strict: false`
- `defineProps` / `defineEmits` for type-safe component interfaces
- Interfaces in PascalCase (`Deal`, `UserProfile`)

## Error Handling

- `try/catch` with `consola.error()` logging
- `createError` from Nuxt for API responses
- Structured error responses with `statusCode`, `statusMessage`, `data`

## Comments

- Only for complex business logic
- In English only
- No obvious comments (avoid "Loop through users")

## State Management

- Pinia stores in `features/*/stores/`
- Persisted via `pinia-plugin-persistedstate`
- Composables for reusable logic in `shared/composables/`
