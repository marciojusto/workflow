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

### AC Coverage
- cobertura completa da current_ac
- clareza dos passos
- exequibilidade técnica

### Code Principles Validation
Valida se o plano respeita cada princípio. Se alguma falhar → is_valid = false com a issue específica:

- **DRY**: O plano propõe reutilizar código existente? Ou cria duplicação desnecessária?
  - Exemplo de falha: "Propor criar função X que já existe em shared/utils/ — reutilizar em vez de duplicar"
- **KISS**: A solução proposta é a mais simples possível para o problema?
  - Exemplo de falha: "Máquina de estados (pending/approved/rejected) para toggle binário — usar boolean"
- **YAGNI**: O plano implementa apenas o que a AC pede? Sem "preparar para o futuro"?
  - Exemplo de falha: "Criar interface genérica para 3 tipos de documento quando só 1 é usado na AC"
- **SOLID**: Cada componente/ficheiro tem responsabilidade única?
  - Exemplo de falha: "Componente DealForm.vue proposto com 500 linhas — extrair lógica de validação para composable"
- **SoC**: Todas as chamadas API respeitam o padrão bsClient? Layers separados?
  - Exemplo de falha: "fetch() direto no template em vez de bsClient → server/api/ → store"

Regras:
- Se o plano não tem secção "Code Principles Adherence" → is_valid = false, issue = "Plano não documenta Code Principles Adherence (secção 5 obrigatória)"
- Se algum princípio é violado pelo plano → is_valid = false, issue específica

Formato:
```json
{
  "is_valid": true,
  "issues": [],
  "code_principles": {
    "dry": "ok" | {"issue": "..."},
    "kiss": "ok" | {"issue": "..."},
    "yagni": "ok" | {"issue": "..."},
    "solid": "ok" | {"issue": "..."},
    "soc": "ok" | {"issue": "..."}
  }
}
```

Se code_principles tiver alguma falha → is_valid = false, e a issue é adicionada a issues[] com prefixo [PRINCIPLE].

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
      - validate Code Principles Adherence (secção 5 do plano):
        - DRY: plano reusa código existente ou cria duplicação?
        - KISS: solução é a mais simples possível?
        - YAGNI: só implementa o que a AC pede?
        - SOLID: responsabilidade única por componente?
        - SoC: bsClient respeitado? Layers separados?
      - se o plano não tem secção "Code Principles Adherence" → is_valid = false
      - se alguma validação de princípio falha → is_valid = false, issue prefixada com [PRINCIPLE]
      - return is_valid + list of issues + code_principles result
   - input: plan, current_ac
   - logic:
     - check if plan covers all aspects of current_ac
     - verify each step is clear and actionable
     - flag any technical issues
     - return is_valid + list of issues