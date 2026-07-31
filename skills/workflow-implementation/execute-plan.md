---
name: execute-plan
version: v1.0.1
description: Gerar implementação baseada no plano
---

# Execute Plan

## Config
requires_mode: code

## Inputs
- plan
- skip_execution: boolean (optional, default: false)
- existing_plan: object (optional, for BUILD mode)

## Output
- implementation

## Instructions
Antes de executar o plano e gerar código, garante que o CLI está em **code mode**.

Se o CLI não estiver em code mode, força a transição para code mode usando o comando `/code` ou equivalente do CLI.

Implementa o plano — cria/alterar os ficheiros necessários.

Regras:
- código limpo
- boas práticas
- coerente com arquitetura moderna

Inclui:
- arquivos criados/modificados
- trechos de código

## Steps

1. check-skip-flag
   - input: skip_execution, existing_plan
   - logic:
     - if skip_execution == true:
         - return: { skipped: true, plan: plan, message: "Execução pulada (modo PLAN)" }
     - if existing_plan:
         - use existing_plan as the plan to execute (BUILD mode)
         - continue to step 2
     - else:
         - continue to step 2

2. ensure-code-mode
   - logic:
     - check if current CLI mode is "code"
     - if not, switch to code mode using CLI command (e.g., /code or mode switch)
     - wait for mode confirmation

3. execute
   - input: plan
   - logic:
     - for each step in plan:
       - create or modify the required files
       - apply code changes
     - return implementation summary with all files changed and code snippets