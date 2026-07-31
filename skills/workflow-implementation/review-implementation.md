---
name: review-implementation
version: v1.0.4
description: Validar se a implementação atende os critérios e segue princípios de código (code-quality primeiro, E2E só se passar)
---

# Review Implementation

## Inputs
- implementation
- current_ac
- acceptance_criteria (all ACs for the ticket)
- project_type (from workflow: nuxt-frontend, java-spring-backend, node-backend)

## Output
- approved
- feedback
- e2e_result

## Instructions
Comparar implementação com critérios de aceitação, verificar utilização do código, verificar princípios de código (DRY, KISS, YAGNI, SOLID, SoC) e executar teste E2E com Playwright.

Verificar que todo o código novo adicionado em execute-plan está a ser utilizado — imports, chamadas de funções, composição de componentes.
O teste E2E pode validar apenas a AC corrente ou todas as ACs do ticket — pedir confirmação ao utilizador.

## Steps

1. ask-user-scope
   - ask user: "Pretende validar apenas a AC corrente ou todas as ACs do ticket?"
   - options:
     - "Apenas a AC corrente (recomendado)"
     - "Todas as ACs do ticket"
   - return selected scope

2. verify-code-usage
   - input: implementation
   - logic:
     - Parse implementation files from execute-plan output
     - For each file added or modified:
       - Check that all new imports are used somewhere in the file
       - Check that newly created functions/components are referenced/called
       - Check that new variable declarations are actually used in the logic
     - Identify any unused code blocks
     - Return list of unused code issues

2.5 verify-code-principles
   - call: skill.code-quality-checker
   - input:
     - files_modified: implementation.files_modified
     - project_type: project_type
     - base_path: implementation.base_path
     - scope: "quick"
     - run_sonar: true
     - sonar_url: "http://localhost:9002"
     - sonar_token: "squ_278bc6fee0a5864b9ce811532790b8eb722668bd"
   - on_error: report_and_continue
   - save_output_as: principles_result

3. check-principles-passed
   - input: principles_result from step 2.5
   - logic:
     - has_violations = principles_result.dry_violations.length > 0 OR principles_result.kiss_violations.length > 0 OR principles_result.yagni_violations.length > 0 OR principles_result.solid_violations.length > 0 OR principles_result.soc_violations.length > 0
     - if has_violations:
         - skip_e2e = true
         - skip_reason = "Code principles failed - skipping E2E to save time"
     - else:
         - skip_e2e = false
   - output: skip_e2e, skip_reason

4. run-playwright-test (only if skip_e2e == false)
   - if skip_e2e == true:
     - skip this step
     - e2e_result = null
   - if skip_e2e == false:
     - call: skill.e2e-validator
     - input:
       - current_ac: current_ac
       - scope: selected scope from step 1 ("current_only" or "all")
       - acceptance_criteria: acceptance_criteria (only needed if scope="all")
     - on_error: report_and_continue

5. evaluate-result
   - input: code_usage_result from step 2, principles_result from step 2.5, e2e_result from step 4, skip_e2e from step 3
   - logic:
     - issues = []
     - principle_issues = []
     - sonar_warning = null

     # Check code usage
     - if code_usage_result.unused_code && code_usage_result.unused_code.length > 0:
         - issues.push("Código não utilizado: " + join(code_usage_result.unused_code))

     # Check code principles (from code-quality-checker skill)
     - has_violations = principles_result.dry_violations.length > 0 OR principles_result.kiss_violations.length > 0 OR principles_result.yagni_violations.length > 0 OR principles_result.solid_violations.length > 0 OR principles_result.soc_violations.length > 0
     - if has_violations:
         - all_violations = []
         - if principles_result.dry_violations.length > 0: all_violations.push("DRY: " + principles_result.dry_violations.length)
         - if principles_result.kiss_violations.length > 0: all_violations.push("KISS: " + principles_result.kiss_violations.length)
         - if principles_result.yagni_violations.length > 0: all_violations.push("YAGNI: " + principles_result.yagni_violations.length)
         - if principles_result.solid_violations.length > 0: all_violations.push("SOLID: " + principles_result.solid_violations.length)
         - if principles_result.soc_violations.length > 0: all_violations.push("SoC: " + principles_result.soc_violations.length)
         - principle_issues.push("Princípios violados: " + all_violations.join(", ") + ". " + principles_result.code_principles_summary)

     # Check SonarQube result
     - if principles_result.sonar_result && principles_result.sonar_result.executed:
         - if principles_result.sonar_result.gate_passed == false:
             - sonar_warning = "SonarQube quality gate falhou (apenas aviso): " + principles_result.sonar_result.quality_gate_status

     # Final decision (handles skip_e2e case)
     - if skip_e2e == true:
         - # Code principles failed, E2E was skipped to save time
         - approved = false
         - feedback = principle_issues + [skip_reason, "Corrigir princípios de código antes de prosseguir"]
     - elif e2e_result == null:
         - # E2E was skipped for another reason
         - approved = false
         - feedback = ["E2E não executado. Verificar causa."]
     - elif e2e_result.passed == true AND issues.length == 0 AND principle_issues.length == 0:
         - approved = true
         - feedback = ["Código verificado e em uso", "Princípios de código verificados", "Teste E2E passou"]
         - if sonar_warning: feedback.push(sonar_warning)
     - elif principle_issues.length > 0:
         - approved = false
         - feedback = principle_issues + ["Corrigir antes de prosseguir"]
     - elif issues.length > 0 AND e2e_result.passed == true:
         - approved = false
         - feedback = ["Código não utilizado: " + issues.join(", ")]
     - else:
         - approved = false
         - feedback = ["Teste E2E falhou: " + e2e_result.error_message] + issues

Formato:
```json
{
  "approved": true,
  "feedback": [
    "Código verificado e em uso",
    "Princípios de código verificados (DRY, SoC, SOLID)",
    "Teste E2E passou: AC validada com sucesso",
    "SonarQube: OK"
  ],
  "e2e_result": {
    "passed": true,
    "screenshot_path": ".workflow/tests/e2e/screenshots/ac_validate.png",
    "error_message": null
  },
  "code_usage_check": {
    "unused_code": [],
    "verified_files": ["src/features/deals/components/DealStatus.vue"]
  },
  "principles_check": {
    "code_principles_passed": true,
    "dry_violations": [],
    "soc_violations": [],
    "solid_violations": [],
    "kiss_violations": [],
    "yagni_violations": [],
    "code_principles_summary": "All code principles verified successfully"
  },
  "sonar_result": {
    "executed": true,
    "gate_passed": true,
    "quality_gate_status": "OK",
    "metrics": {
      "bugs": 0,
      "code_smells": 12,
      "coverage": 78.5,
      "duplications": 3.2,
      "lines_of_code": 5420,
      "maintainability": "A",
      "reliability": "A",
      "security": "A"
    },
    "new_issues": 0,
    "url": "http://localhost:9000/dashboard?id=hyperfront",
    "scanned_at": "2026-05-04T10:30:00Z"
  }
}
```