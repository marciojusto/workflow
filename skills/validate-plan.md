---
name: validate-plan
version: v1.0.0
description: Garantir que o plano cobre todos os critérios
---

# Validate Plan

## Config
requires_mode: plan

## Inputs
- plan
- current_ac

## Output
- is_valid
- issues

## Instructions
Antes de validar o plano, garante que o CLI está em **plan mode**.

Se o CLI não estiver em plan mode, força a transição para plan mode usando o comando `/plan` ou equivalente do CLI.

Verifica:
- cobertura completa da current_ac
- clareza dos passos
- exequibilidade técnica

Formato:
```json
{
  "is_valid": true,
  "issues": []
}
```

## Steps

1. ensure-plan-mode
   - logic:
     - check if current CLI mode is "plan"
     - if not, switch to plan mode using CLI command (e.g., /plan or mode switch)
     - wait for mode confirmation

2. validate
   - input: plan, current_ac
   - logic:
     - check if plan covers all aspects of current_ac
     - verify each step is clear and actionable
     - flag any technical issues
     - return is_valid + list of issues