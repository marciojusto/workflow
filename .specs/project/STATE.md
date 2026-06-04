# Session State

## Decisions

- API calls go through `bsClient` → `server/api/` endpoints → Vue components (SoC)
- All user-facing strings from i18n files
- Pinia stores in `features/*/stores/`, composables in `shared/composables/`

## Blockers

- (none currently)

## Lessons

- DPP popup must be handled in Playwright tests (click "sending by email")
- Postal code 35309 for test data
- Proposal phase button enabled after clicking "send secci"

## Preferences

- Use `kilo/minimax/minimax-m2.7` as default for miles-expert
- Escalate to `kilo/deepseek/deepseek-v4-pro` for complex/ambiguous tickets
- Prefer structured trace-based E2E test generation over linear Playwright code
