---
name: workflow-implementation
version: v1.3.0
description: User history implementation workflow. Thin orchestrator that delegates each step to independent sub-skills. Hybrid flow: uses tlc-spec-driven for SPECIFY+DESIGN, native tasks for EXECUTE. Supports JIRA/Redmine integration or standalone mode with grill+spike.
---

# Workflow Implementation

## Flow

```
mode-selection → detect-project-type → detect-task-tracker
  → (JIRA/Redmine) extract-jira-ticket → analyze-with-expert (optional)
  → (Standalone)   grill+spike → tlc-spec-driven direto
  → spec-driven-planning (tlc-spec-driven SPECIFY+DESIGN)
  → teach (optional, based on complexity)
  → check-existing-plan
  → create-plan → validate-plan → request-human-approval
  → execute-plan → run-tests → generate-regression-test
  → review-implementation → run-code-quality-checks
  → run-regression-tests → log-history
  → loop next AC
```

## Step 0: mode-selection

Ask user: `nova`, `bug`, `validar`, `continuar`. Store in context.

## Step 0.1: detect-project-type

Detect project type from file indicators:
- `pom.xml` → `java-spring-backend`
- `package.json` + `playwright.config.ts` → `nuxt-frontend`
- `package.json` (no playwright) → `node-backend`

Check `AGENTS.md` if exists. Check app running for frontend if validar mode.

## Step 0.2: detect-task-tracker (NEW)

Ask the user:
```
Seu projeto usa algum controlador de tarefas?
1. JIRA
2. Redmine
3. Outro (especifique)
4. Não, projeto pessoal/sem ferramenta externa
```

Store selection in context as `task_tracker_type`:
- `jira` → proceed to Step 0.3 (extract-jira-ticket)
- `redmine` → proceed to Step 0.3 (extract-jira-ticket with Redmine adapter)
- `other` → ask for tracker name/API config, then proceed to Step 0.3
- `none` → skip to Step 0.5 (grill+spike → tlc-spec-driven direto)

**CRITICAL**: This step is mandatory. Do not assume the user has JIRA configured.

## Step 0.3: extract-jira-ticket (CONDITIONAL)

**Only if task_tracker_type is jira/redmine/other.**

Invoke: `extract-jira-ticket.md`
→ output: title, description, ACs, current_ac, total_ac_count, all_done, attachments, links, linked_issues, existing_plan, rag_resources

If `task_tracker_type == none`, skip this step entirely.

## Step 0.4: check-all-done (CONDITIONAL)

**Only if task_tracker_type is jira/redmine/other.**

If `validar` → go to step 1 (validate-branch)
If `all_done` → ask if user wants to implement another ticket → loop or STOP
Otherwise → continue

If `task_tracker_type == none`, skip this step.

## Step 0.5: context-gathering (STANDALONE MODE)

**Only if task_tracker_type == none.**

For projects without a task tracker, gather context from:

1. **Grill output** (if grill mode was selected):
   - ADRs: `.specs/grill/{topic}/adrs/`
   - Glossary: `.specs/grill/{topic}/glossary/glossary.md`
2. **Spike output** (if available):
   - Spike report: `.specs/grill/{topic}/spike-report.md`
   - Spike data: `.specs/grill/{topic}/spike-*.{csv,json}`
3. **User input**:
   - Ask user to describe what needs to be implemented
   - Ask for acceptance criteria (if any)
   - Capture any attachments/links provided

Output: `task_context` object with:
- title
- description
- acceptance_criteria
- current_ac
- total_ac_count
- adrs_path
- spike_report_path
- existing_plan

## Step 0.6: analyze-with-expert (OPTIONAL)

**For both JIRA and standalone modes.**

Ask user: "Deseja análise técnica com o expert de domínio configurado? (s/n)"
- If `sim` → invoke @business-expert with task context
- If `não` → skip, proceed directly to spec-driven-planning

**CRITICAL**: Expert is optional. Never block the workflow if expert is not available.

## Step 1: spec-driven-planning (tlc-spec-driven — hybrid)

After context gathering (from JIRA or standalone), invoke tlc-spec-driven skill:

1. **SPECIFY** (always): Convert context into `.specs/features/{ticket_id}/spec.md`
   - Extract requirement IDs from acceptance criteria or user description
   - Document gray areas and decisions
   - Context: from Step 0.3 (JIRA) or Step 0.5 (standalone) + Step 0.6 (expert if used)
2. **DESIGN** (if Large/Complex): Generate `.specs/features/{ticket_id}/design.md`
   - Architecture decisions, component breakdown
   - Skip if change is straightforward (auto-sized by tlc-spec-driven)
3. Output: `spec.md` (always) + `design.md` (optional)

**Scope:** For all modes: nova, bug, continuar, standalone.

## Step 1.5: teach (OPTIONAL)

After spec-driven-planning, evaluate complexity:

| Signal | Points |
|--------|--------|
| Files modified > 3 | +1 |
| New domain concepts introduced | +1 |
| spec.md length > 150 lines OR requirements > 5 | +1 |
| Business expert was NOT consulted | +1 |
| Cross-module changes | +1 |
| New entities/DTOs/controllers | +1 |

If score >= 2 → recommend teach to user:
```
📚 Este plano tem complexidade média/alta.
Queres que eu gere uma explicação didática (teach) antes de executar? (s/n)
```

If user accepts → invoke `teach` skill, save to `.specs/teach/{ticket_id}/`

**CRITICAL**: Teach is optional. Do not block execution if user declines.

## Step 2: validate-branch (validar mode only)

Invoke `e2e-validator` with all ACs → capture screenshots → JSON report → wiki note → STOP

## Step 3: check-existing-plan

If plan exists → skip to step 6 (request-human-approval)
Otherwise → create plan first

## Step 4: create-plan

Invoke: `create-plan.md`
Input: title, description, current_ac, ticket_id, current_ac_index
Input (if spec-driven-planning ran): requirement IDs from `.specs/features/{ticket_id}/spec.md`
Output: plan object with traceable requirement IDs

**Code Principles**: O plano DEVE incluir:
1. Secção 5 "Code Principles Adherence" — DRY/KISS/YAGNI/SOLID/SoC
2. Secção 6 "Clean Code Compliance" — Funções <20 linhas, nomes descritivos, early return
3. Secção 7 "Testing Strategy" — TDD, Given-When-Then, Arrange-Act-Assert

## Step 5: validate-plan

Invoke: `validate-plan.md`
Input: plan, current_ac

**Code Principles**: validate-plan verifica:
1. Secção 5 (DRY/KISS/YAGNI/SOLID/SoC) — issue prefixada com `[PRINCIPLE]`
2. Secção 6 (Clean Code) — issue prefixada com `[CLEAN_CODE]`
3. Secção 7 (Testing) — issue prefixada com `[TESTING]`

Se alguma secção não existe ou se algum princípio é violado → is_valid = false.
If invalid → loop back to create-plan (max 2 iterations)

## Step 6: request-human-approval

Invoke: `request-human-approval.md`
Input: plan, current_ac
**CRITICAL: No code changes before approved == true**

## Step 7: execute-plan

Invoke: `execute-plan.md`
Input: approved plan
**ONLY after step 6 approved**

## Step 8: run-tests

If `nuxt-frontend` → invoke `e2e-validator` with current AC
   → Capture `test_trace` from e2e-validator output
If `java-spring-backend` → `./mvnw test`
If `node-backend` → `npm test`
If failed → loop to create-plan

## Step 8.5: generate-regression-test

Source: `test_trace` captured from e2e-validator output in step 8.

If `test_trace` is available:
  → Save trace to `.workflow/traces/{ticket_id}_ac{ac_index}.json`
  → Run: `python3 ~/Development/teamwill/mobilize/workflow/scripts/trace-to-playwright.py --trace .workflow/traces/{ticket_id}_ac{ac_index}.json --output playwright/tests/regression/{ticket_id}_ac{ac_index}.spec.ts --run --validate`

Otherwise, create based on project_type:
- Frontend: Playwright spec from template
- Java: JUnit test class
- Node: Jest/Mocha test file

## Step 9: review-implementation

Invoke: `review-implementation.md`
Input: implementation, current_ac, acceptance_criteria
If rejected → loop to create-plan

## Step 9b: run-code-quality-checks

Per project_type:
- Frontend: `npm run lint` then SonarQube
- Java: `./mvnw verify -DskipTests` then SonarQube
- Node: `npm run lint` then SonarQube

## Step 9c: run-regression-tests

Per project_type:
- Frontend: `npx playwright test tests/regression/`
- Java: `./mvnw test -Dtest="*RegressionTest,*IntegrationTest"`
- Node: `npm test -- tests/regression/`

## Step 9d: log-history

Invoke: `log-history.md`
Input: ticket_id, current_ac_index, current_ac, implementation_summary, regression_test_result
→ loop to step 0.2 (detect-task-tracker) for next AC

---

## Modes Summary

| Mode | JIRA/Redmine | Expert | Teach | Description |
|------|--------------|--------|-------|-------------|
| `nova` | Optional | Optional | Auto-recommended | New feature from scratch |
| `bug` | Optional | Optional | Auto-recommended | Fix a bug |
| `validar` | Optional | N/A | No | Run E2E validation only |
| `continuar` | Optional | Optional | Auto-recommended | Continue existing work |

## Task Context Format (Standalone Mode)

When no task tracker is used, the task context object:

```json
{
  "title": "User-provided title",
  "description": "User-provided description",
  "acceptance_criteria": ["AC1", "AC2"],
  "current_ac": "AC1",
  "current_ac_index": 0,
  "total_ac_count": 2,
  "adrs_path": ".specs/grill/{topic}/adrs/",
  "spike_report_path": ".specs/grill/{topic}/spike-report.md",
  "existing_plan": { "found": false }
}
```
