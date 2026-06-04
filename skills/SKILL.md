---
name: workflow-jira-ticket
version: v1.0.6
description: User history implementation workflow with auto-detect project type and code principles verification (code-quality-first in review-implementation)
---

# Workflow Jira Ticket

## Config
retry_strategy:
  validate-plan: 2
  review-implementation: 2

## Operation Modes

### Input Selection
Ask user to select one of four modes:
- `nova` - Full implementation for story ticket with ACs
- `bug` - Implement bug fix for ticket without ACs
- `validar` - Validate existing branch (checklist + screenshots only)
- `continuar` - Resume incomplete implementation from history

## Project Type Detection
The workflow automatically detects the project type based on file indicators:

| Detected Type | File Indicator | Test Framework | Test Command |
|--------------|----------------|-----------------|---------------|
| nuxt-frontend | package.json + playwright.config.ts | Playwright | npx playwright test |
| java-spring-backend | pom.xml + src/test/java | JUnit/Maven | ./mvnw test |
| node-backend | package.json (no playwright) | Jest/Mocha | npm test |

Default project paths:
- Frontend: ~/Development/teamwill/mobilize/hyperfront
- Backend (Java): ~/Development/teamwill/mobilize/deal-bs
- Backend (Node): detected from project root

## Instructions
Workflow iterativo que implementa uma Acceptance Criteria (AC) de cada vez.
Após cada AC concluída, o histórico é actualizado e a próxima AC é carregada.
O workflow termina quando todas as ACs estão concluídas — nesse momento pergunta ao utilizador se quer implementar outro ticket.

## Input
- jira_ticket_id

## Steps

0. mode-selection
    - Ask user to select: nova/bug/validar/continuar
    - Store mode in context

0. detect-project-type
    - Check for pom.xml in project root:
      ```bash
      ls -la pom.xml 2>/dev/null || echo "not_found"
      ```
    - If pom.xml exists → project_type = "java-spring-backend"
    - If package.json + playwright.config.ts exists → project_type = "nuxt-frontend"
    - If package.json (no playwright) → project_type = "node-backend"
    - Store project_type in context for all subsequent steps

0.1 check-project-guidelines
    - check if AGENTS.md exists in project root:
      ```bash
      cat AGENTS.md
      ```
    - if exists, read and apply all guidelines from AGENTS.md
    - guidelines include: code style, language (English), naming conventions, patterns, etc.

0.2 check-app-running (only for validate mode AND nuxt-frontend)
    # Only check for frontend - backend uses Maven/Gradle
    if project_type == "nuxt-frontend":
      - Check if http://localhost:3000 is accessible:
        ```bash
        curl -f http://localhost:3000 >/dev/null 2>&1 && echo "running" || echo "not_running"
        ```
      - if not_running: ask user "O servidor não está rodando. Execute 'npm run dev' e pressione Enter quando estiver pronto"
    # Backend (Java/Node) - Maven/Gradle handles its own server
    if project_type == "java-spring-backend" or project_type == "node-backend":
      - Skip - backend tests don't require running app

0.3 extract-jira-ticket.md
    input:
      jira_ticket_id: jira_ticket_id
    output:
      - title
      - description
      - acceptance_criteria
      - current_ac
      - current_ac_index
      - total_ac_count
      - all_done
      - attachments
      - links
      - linked_issues
      - existing_plan
      - rag_resources

0.4 check-all-done by mode
    - if mode == "validar":
        - go_to step 1 (validate-branch)
    - if mode == "continuar" and all_done == true:
        ask user: "Todas as ACs [{total_ac_count}] já foram concluídas para {jira_ticket_id}. Deseja implementar outro ticket?"
        - if yes: user provides new jira_ticket_id → go_to step 0.3
        - if no: STOP workflow
    - if mode == "nova" or mode == "bug" and all_done == true:
        ask user: "Todas as ACs [{total_ac_count}] foram concluídas para {jira_ticket_id}. Deseja implementar outra issue?"
        - if yes: user provides new jira_ticket_id → go_to step 0.3
        - if no: STOP workflow
    - if all_done == false: continue to step 2

1. validate-branch (only for validar mode)
    - execute e2e-validator with all ACs from ticket
    - capture screenshots for each AC
    - generate JSON report with:
      - passed: boolean
      - errors[]: detailed error list
      - suggestions[]: fix suggestions  
      - diff: `git diff develop...HEAD --stat`
      - screenshots[]: captured images
      - ac_results: map AC id -> pass/fail
    - create wiki note with report
    - STOP workflow

2. check-existing-plan
    - if existing_plan.found == true AND mode == "continuar":
      - plan = existing_plan.content
      - plan_path = existing_plan.path
      - go_to step 6 (execute-plan)
    - if existing_plan.found == true AND mode == "build":
      - plan = existing_plan.content
      - go_to step 6 (execute-plan)
    - else: (mode == "nova" or mode == "bug") and no existing plan:
      - ERROR: "Plan not found. Run AUTO mode through orchestrator first."
      - STOP

3. [REMOVED] create-plan — plan is generated by miles-expert and validated by review-plan

4. [REMOVED] validate-plan — validation is done by review-plan agent

5. [REMOVED] request-human-approval — approval was obtained after review-plan step

6. execute-plan.md
    input:
      - plan
    **Plan comes pre-validated from miles-expert → review-plan pipeline**

7. coherence-checker
    description: Validate implementation coherence before running tests
    input:
      - implementation (from execute-plan)
      - plan
      - project_type
    agent: @coherence-checker
    if coherent == false:
      - report issues to user
      - go_to: miles-expert (fix coherence issues)

7b. run-tests
    description: Run tests - dynamically selected based on project_type
    input:
      - current_ac
      - acceptance_criteria
      - project_type (from step 0)

    # Frontend (Nuxt/Vue with Playwright)
    if project_type == "nuxt-frontend":
      - call: skill.e2e-validator
      - input: current_ac, acceptance_criteria (scope="current_only")
      - if passed == false:
        - report failures to user
        - go_to: miles-expert (fix implementation)
      - output: passed, screenshot_path, error_message

    # Backend (Java/Spring with Maven)
    if project_type == "java-spring-backend":
      - execute: cd ~/Development/teamwill/mobilize/deal-bs && ./mvnw test -Dtest=*Test 2>&1
      - if tests fail:
        - report failures to user
        - go_to: miles-expert (fix implementation)
      - output: passed, test_report_path, error_message

    # Backend (Node.js with Jest/Mocha)
    if project_type == "node-backend":
      - execute: npm test 2>&1
      - if tests fail:
        - report failures to user
        - go_to: miles-expert (fix implementation)
      - output: passed, test_report_path, error_message

7.5 generate-regression-test
    description: Generate regression test after successful validation (project-specific)
    input:
      - jira_ticket_id
      - current_ac
      - validation_result (from step 7)
      - project_type (from step 0)

    # Frontend: Playwright spec
    if project_type == "nuxt-frontend":
      - template_path: ~/Development/teamwill/mobilize/playwright/tests/regression/template.spec.ts
      - output_path: ~/Development/teamwill/mobilize/playwright/tests/regression/{ticket_id}_ac{current_ac_index}.spec.ts
      - copy template.spec.ts to output path
      - replace placeholders:
        - {ticket_id} → jira_ticket_id
        - {ac_description} → short description of current_ac
        - {ac_text} → full current_ac text
        - {flow_steps} → steps executed in validation
        - {assertions} → key assertions from validator

    # Backend (Java): JUnit test in src/test/java
    if project_type == "java-spring-backend":
      - output_path: {project_root}/src/test/java/com/mfs/mpp/integrationlayer/regression/{TicketId}RegressionTest.java
      - create JUnit 5 test class with @Test annotations
      - include test methods for each AC
      - use @DisplayName for AC descriptions

    # Backend (Node): Jest/Mocha test
    if project_type == "node-backend":
      - output_path: {project_root}/tests/regression/{ticket_id}.test.js
      - create test file with describe/test blocks
          - {screenshot_path} → validation screenshot path
          - {flow_steps} → steps executed in validation
          - {assertions} → key assertions from validator
        - test runs automatically in step 8c (run-regression-tests)
      - if passed == false:
        - skip generation (test will be created after fix + re-validation)

8. review-implementation.md
    input:
      - implementation
      - current_ac
      - acceptance_criteria (for playwright scope="all")
    if approved == false:
      go_to: miles-expert (fix implementation issues)

8b. run-code-quality-checks
    input:
      - project_type (from step 0)

# Frontend (Nuxt/Vue)
    if project_type == "nuxt-frontend":
      - run ESLint to check for code issues:
        ```
        npm run lint
        ```
      - if ESLint fails:
        - report errors to user
        - fix issues automatically if possible: `npm run lint:fix`
        - if still failing: go_to create-plan.md
      - run SonarQube analysis (optional, requires Docker):
        - First, ensure SonarQube is running:
          ```
          docker compose -f .workflow/docker/docker-compose.yml up -d sonarqube
          ```
        - Run: .workflow/docker/scan-hyperfront.sh (auto-detects token)
        - if critical: go_to create-plan.md

# Backend (Java/Spring)
    if project_type == "java-spring-backend":
      - run SpotBugs/Checkstyle via Maven:
        ```
        cd ~/Development/teamwill/mobilize/deal-bs
        ./mvnw verify -DskipTests -Dspotbugs.skip=false
        ```
      - if analysis fails:
        - report issues to user
        - if critical: go_to create-plan.md
      - run SonarQube analysis (optional):
        - Run: .workflow/docker/scan-deal-bs.sh
        - if critical: go_to create-plan.md
      - run SonarQube analysis (optional):
        - Run: .workflow/docker/scan.sh
        - if critical: go_to create-plan.md

# Backend (Node.js)
    if project_type == "node-backend":
      - run ESLint:
        ```
        npm run lint
        ```
      - if fails: go_to create-plan.md
      - run SonarQube analysis (optional):
        - Run: .workflow/docker/scan-hyperfront.sh (ou criar scan-node.sh específico)

8c. run-regression-tests
    description: Executa testes de regressão - dinâmico baseado no project_type
    input:
      - project_type (from step 0)
    on_error: report_and_continue

    # Frontend (Nuxt/Vue with Playwright)
    if project_type == "nuxt-frontend":
      command: |
        cd ~/Development/teamwill/mobilize/playwright
        npx playwright test tests/regression/ --reporter=html --output=reports 2>&1

    # Backend (Java/Spring with Maven)
    if project_type == "java-spring-backend":
      command: |
        cd ~/Development/teamwill/mobilize/deal-bs
        ./mvnw test -Dtest="*RegressionTest,*IntegrationTest" 2>&1

    # Backend (Node.js with Jest/Mocha)
    if project_type == "node-backend":
      command: |
        npm test -- tests/regression/ 2>&1

    output:
      - regression_passed
      - regression_failed_count
      - regression_report_path

    on_result:
      - if regression_failed_count > 0:
          - include in log_history: "Regression tests FAILED: {regression_failed_count} failures"
          - attach report path: {regression_report_path}
      - if regression_failed_count == 0:
          - include in log_history: "Regression tests: PASSED"

8d. log-history.md
    input:
      - jira_ticket_id
      - current_ac_index
      - current_ac
      - implementation_summary
      - regression_test_result (from step 8c)
    → go_to step 0.3 (carregar próxima AC)

## Nota
O max_iterations é determinado dinamicamente por `total_ac_count` para evitar loops infinitos.