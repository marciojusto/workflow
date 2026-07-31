# Test Automation on Project Start

Two approaches for running tests automatically when the project starts, tailored for different use cases.

---

## Option 1: CI/CD — `predev` / `prebuild` Hook (in CI only)

**Goal:** Fail the build if tests don't pass. No deployment without green tests.

**Approach:** npm `pre` scripts are placed **only in the CI workflow file** — not in the local `package.json`. This way local devs are unaffected.

### Changes to `package.json` — development-only

```json
{
  "scripts": {
    "dev": "nuxt dev",
    "dev:test": "concurrently \"vitest\" \"nuxt dev\"",
    "build": "nuxt build && npm run copy-scripts",
    "start": "node .output/server/index.mjs",
    "test": "vitest"
  }
}
```

### Changes to CI pipeline (e.g. `.github/workflows/ci.yml`)

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run tests (pre-build gate)
        run: npm run test

      - name: Build
        run: npm run build
```

### How it works

| Environment | Command | What happens |
|---|---|---|
| **Local dev** | `npm run dev` | Nuxt starts immediately — no tests |
| **Local dev (TDD)** | `npm run dev:test` | Vitest (watch) + Nuxt start together |
| **CI server** | `npm run build` | `npm ci` installs deps → CI runs `npm run test` → then build |

The `prebuild` hook is **not** in `package.json`. Instead, CI runs `test` explicitly as a separate step before `build`. This is cleaner because:
- Locally, `npm run dev` never blocks on tests
- CI controls exactly when tests run and can fail the pipeline
- Developers can opt into tests with `dev:test` when they want

### Behaviour

| Scenario | Result |
|---|---|
| Tests pass in CI | Build proceeds |
| Tests fail in CI | Pipeline fails, no deployment |
| Local `npm run dev` | Never runs tests |
| Local `npm run dev:test` | Tests + server start together |

### Pros
- No local impact — `npm run dev` never blocks
- CI controls exactly when tests run and can gate the build
- Developers can opt into TDD mode when they want

### Cons
- Requires a CI workflow file (e.g. GitHub Actions)
- `concurrently` needed for the local TDD mode

---

## Option 2: Development — `concurrently` + Watch Mode (opt-in)

**Goal:** Fast feedback loop. Tests re-run automatically on file changes without blocking the dev server.

**Approach:** Run Vitest in watch mode and Nuxt dev server simultaneously using `concurrently`.

### Install dependency

```bash
npm install -D concurrently
```

### Changes to `package.json`

```json
{
  "scripts": {
    "dev": "nuxt dev",
    "dev:test": "concurrently \"vitest\" \"nuxt dev\"",
    "test": "vitest"
  }
}
```

### How it works

```bash
# Normal dev (no tests) — default, never blocks
npm run dev

# Dev with tests running in background (watch mode) — opt-in
npm run dev:test
```

Both processes start **at the same time**. Vitest watches for file changes and re-runs affected tests automatically.

### Output in terminal

```
[nuxt]  Nuxt 3.17.5 started on http://localhost:3000
[vite]  Vite client built in 58ms

 ✓ 3 tests passed (watch mode active)
   ↻ Re-running on changes...
```

### Pros
- Dev server starts immediately (no waiting)
- Tests re-execute on every save — instant feedback
- No impact on normal `npm run dev` workflow
- Team members can opt in/out easily

### Cons
- Requires installing `concurrently` (one-time, low overhead)
- Terminal shows output from two processes mixed together
- `vitest --watch` keeps running in background — must be stopped explicitly

### Recommended Vitest config tweaks

In `vitest.config.ts`, enable watch by default for this mode:

```ts
export default defineVitestConfig({
    test: {
        environment: 'nuxt',
        globals: true,
        watch: true, // ← already default in Vitest
        setupFiles: ['tests/mute-console.ts'],
        coverage: {
            provider: 'v8',
            reporter: ['lcov', 'text', 'html'],
            reportsDirectory: './coverage',
            include: ['server/**', 'features/**', 'shared/**', 'composables/**', 'utils/**'],
            exclude: ['node_modules/**', '.nuxt/**', '.output/**', 'tests/**']
        }
    }
})
```

---

## Summary comparison

| Aspect | Option 1 (CI/CD) | Option 2 (Dev) |
|---|---|---|
| **Trigger** | CI pipeline runs `test` explicitly | `npm run dev:test` |
| **Mode** | `vitest run` (once, blocks on result) | `vitest --watch` (continuous) |
| **Blocks server** | Yes (fails CI if tests fail) | No |
| **Feedback speed** | Slow (waits for all tests) | Fast (per-file, on save) |
| **Extra packages** | None | `concurrently` |
| **Use case** | CI/CD pipelines, pre-deploy | Daily development |

---

## Suggested rollout

**Local development** (default — no test blocking):
- `npm run dev` → Nuxt starts immediately, tests are never in the way
- `npm run dev:test` → Optional TDD mode, opt-in per developer

**CI/CD pipeline** (the only place where test gating lives):
- CI runs `npm run test` explicitly before `npm run build`
- If tests fail → pipeline fails → nothing deploys
- Local `package.json` stays clean — no `predev`/`prebuild` hooks

---

## Files to modify

| File | Change |
|---|---|
| `package.json` | Add `dev:test` script + install `concurrently` as dev dependency |
| `.github/workflows/ci.yml` | Add `npm run test` step before `npm run build` |
| `vitest.config.ts` | No changes needed |
| *(optional)* `README.md` | Document the two modes for new developers |

