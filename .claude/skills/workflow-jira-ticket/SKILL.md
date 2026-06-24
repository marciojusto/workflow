---
name: workflow-jira-ticket
version: v1.2.0
description: User history implementation workflow. Thin orchestrator that delegates each step to independent sub-skills. Hybrid flow: uses tlc-spec-driven for SPECIFY+DESIGN, native tasks for EXECUTE.
---

# Workflow Jira Ticket

## Flow

```
mode-selection → detect-project-type → extract-jira-ticket
  → validate-branch (if validar) STOP
  → analyze-with-miles-expert (if nova/bug/continuar)
  → spec-driven-planning (NEW — tlc-spec-driven SPECIFY+DESIGN)
  → check-existing-plan
  → create-plan (with requirement IDs from spec.md) → validate-plan → request-human-approval
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

## Step 0.3: extract-jira-ticket
Invoke: `extract-jira-ticket.md`
→ output: title, description, ACs, current_ac, total_ac_count, all_done, attachments, links, linked_issues, existing_plan, rag_resources

## Step 0.4: check-all-done
If `validar` → go to step 1 (validate-branch)
If `all_done` → ask if user wants to implement another ticket → loop or STOP
Otherwise → continue

## Step 0.5: analyze-with-miles-expert
If `nova/bug/continuar` → invoke @miles-expert with ticket data for deep domain analysis
If `validar` → skip

## Step 0.6: spec-driven-planning (tlc-spec-driven — hybrid)
After miles-expert analysis, invoke tlc-spec-driven skill for structured specification:

1. **SPECIFY** (always): Convert Jira ticket into `.specs/features/{ticket_id}/spec.md`
   - Extract requirement IDs from ACs
   - Document gray areas and decisions
   - Context: ticket data from step 0.3 + miles-expert analysis from step 0.5
2. **DESIGN** (if Large/Complex): Generate `.specs/features/{ticket_id}/design.md`
   - Architecture decisions, component breakdown
   - Skip if change is straightforward (auto-sized by tlc-spec-driven)
3. Output: `spec.md` (always) + `design.md` (optional) — requirement IDs feed into Step 3 (create-plan)

**Scope:** Only for nova/bug/continuar modes. Skip for validar.

## Step 1: validate-branch (validar mode only)
Invoke `e2e-validator` with all ACs → capture screenshots → JSON report → wiki note → STOP

## Step 2: check-existing-plan
If plan exists → skip to step 5 (request-human-approval)
Otherwise → create plan first

## Step 3: create-plan
Invoke: `create-plan.md`
Input: title, description, current_ac, jira_ticket_id, current_ac_index
Input (if spec-driven-planning ran): requirement IDs from `.specs/features/{ticket_id}/spec.md`
Output: plan object with traceable requirement IDs (e.g. `req: RQ-001`)
**Code Principles**: O plano DEVE incluir a secção "Code Principles Adherence" (secção 5) que documenta como DRY/KISS/YAGNI/SOLID/SoC serão respeitados. Sem esta secção o validate-plan rejeitará o plano.

## Step 4: validate-plan
Invoke: `validate-plan.md`
Input: plan, current_ac
**Code Principles**: validate-plan verifica secção 5 do plano (DRY/KISS/YAGNI/SOLID/SoC). Se a secção não existe ou se algum princípio é violado → is_valid = false, issue prefixada com `[PRINCIPLE]`.
If invalid → loop back to create-plan (max 2 iterations)

## Step 5: request-human-approval
Invoke: `request-human-approval.md`
Input: plan, current_ac
**CRITICAL: No code changes before approved == true**

## Step 6: execute-plan
Invoke: `execute-plan.md`
Input: approved plan
**ONLY after step 5 approved**

## Step 7: run-tests
If `nuxt-frontend` → invoke `e2e-validator` with current AC
If `java-spring-backend` → `./mvnw test`
If `node-backend` → `npm test`
If failed → loop to create-plan

## Step 7.5: generate-regression-test
If spec-trace (`test_trace` JSON from e2e-runner) is available:
  → `python3 ~/Development/teamwill/mobilize/workflow/scripts/trace-to-playwright.py --trace <trace.json> --output <spec.ts> --run --validate`

Otherwise, create based on project_type:
- Frontend: Playwright spec from template
- Java: JUnit test class
- Node: Jest/Mocha test file

## Step 8: review-implementation
Invoke: `review-implementation.md`
Input: implementation, current_ac, acceptance_criteria
If rejected → loop to create-plan

## Step 8b: run-code-quality-checks
Per project_type:
- Frontend: `npm run lint` then SonarQube
- Java: `./mvnw verify -DskipTests` then SonarQube
- Node: `npm run lint` then SonarQube

## Step 8c: run-regression-tests
Per project_type:
- Frontend: `npx playwright test tests/regression/`
- Java: `./mvnw test -Dtest="*RegressionTest,*IntegrationTest"`
- Node: `npm test -- tests/regression/`

## Step 8d: log-history
Invoke: `log-history.md`
Input: jira_ticket_id, current_ac_index, current_ac, implementation_summary, regression_test_result
→ loop to step 0.3 for next AC
