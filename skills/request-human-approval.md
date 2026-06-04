---
name: request-human-approval
version: v1.0.1
description: Solicitar aprovação humana antes de executar o plano
---

# Request Human Approval

## Inputs
- plan
- current_ac (acceptance criteria being implemented)
- validation_result (from review-plan)

## Output
- approved: boolean

## CRITICAL RULES
1. **NUNCA execute código antes de approved == true**
2. **NUNCA modifique arquivos antes de approved == true**
3. **Aguarde resposta explícita do utilizador**

## Instructions

### Step 1: Display Information
Mostre ao utilizador:
- **Ticket**: {jira_ticket_id}
- **Current AC**: {current_ac}
- **Plano**: exiba o conteúdo completo do plano
- **Validation Result**: resultado do review-plan

### Step 2: Request Explicit Approval
Peça confirmação explícita usando uma destas palavras:
- `approve` - para prosseguir com a execução
- `reject` - para rejeitar e enviar feedback ao miles-expert

### Step 3: Wait for Response
- **AGUARDE** a resposta do utilizador
- **NÃO prossiga** sem resposta explícita
- **NÃO execute** nenhuma mudança de código enquanto aguarda

### Step 4: Return Result
Responda em JSON:
```json
{
  "approved": true  // ou false baseado na resposta do utilizador
}
```

## Example Output
```
==========================================
APROVAÇÃO NECESSÁRIA
==========================================
Ticket: MMH-1373
Current AC: 1/3 - O sistema deve permitir adicionar múltiplos contactos

PLANO:
[exibir plano completo]

VALIDAÇÃO: ✅ Válido

Por favor, responda com:
- "approve" para continuar
- "reject" para voltar ao plano
==========================================
```