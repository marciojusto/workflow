# MMH-1483: Corrigir downPayment no Financing Tab

## Problem Statement

No financing tab, quando o utilizador edita o campo `downPayment` e perde o foco (blur), o valor é enviado como campo a raiz do payload (`{ downpayment: "1000" }`), mas o backend (`RequestCalculateDeal`) não reconhece este campo — espera `financingAdjustment.downpayment`. Além disso, `quotationTemplate` é sempre incluído no payload, forçando o backend a tratar como "QT Change", o que remove `financingAdjustment` e `productConfiguration`.

Resultado: o MMP nunca recebe o downPayment como serviço sintético, e o cálculo não reflete o valor introduzido.

---

## Goals

- [ ] DownPayment no financing tab aciona cálculo correto ao perder foco
- [ ] Payload envia `financingAdjustment.downpayment` (nunca a raiz)
- [ ] QuotationTemplate só enviado quando bareme realmente alterado
- [ ] TradeInValue e ecoBonus continuam a funcionar sem regressão

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Alterar backend (PayloadBuilder, DealServiceImpl) | Backend já processa `financingAdjustment` corretamente; problema é 100% frontend |
| Alterar Asset tab | Asset tab já funciona corretamente; não é objetivo desta tarefa |
| Suporte a múltiplos options com valores diferentes | Fora do scope; `enqueueCalculation` já serializa |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
|----------------------|----------------|-----------|------------|
| TradeIn no financing tab está disabled | Não tratar tradeIn no financing tab | Confirmado pelo utilizador | ✅ y |
| MMP responde sempre com mesma estrutura | Não alterar tratamento de resposta | Investigado com miles-expert | ✅ y |
| `ecoBonus` no financing tab lido do asset store | Manter comportamento atual | `buildFinancingAdjustment` já inclui ecoBonus do asset store | ✅ y |

**Open questions:** none — all resolved or logged above.

---

## User Stories

### P1: DownPayment no Financing Tab Aciona Cálculo ⭐ MVP

**User Story**: Como utilizador, quero que ao editar o downPayment no financing tab e perder o foco, o sistema recalcule a prestação mensal incluindo o valor introduzido.

**Why P1**: Sem isto, o utilizador introduz downPayment mas o cálculo ignora-o completamente — funcionalidade essencial para leasing.

**Acceptance Criteria**:

1. WHEN utilizador edita downPayment e perde foco THEN frontend SHALL extrair `downpayment` do deltaPayload e incluir em `financingAdjustment`
2. WHEN `sendScalarDelta("downpayment", 1000)` é chamado THEN payload enviado ao backend SHALL conter `financingAdjustment.downpayment = "1000"` e NÃO conter `downpayment` a raiz
3. WHEN payload contém apenas financial delta (`downpayment`) THEN `quotationTemplate` NÃO SHALL ser enviado no payload
4. WHEN backend recebe `financingAdjustment.downpayment` THEN SHALL criar serviço sintético "Down payment at dealer" com valor correto
5. WHEN MMP retorna resposta THEN monthlyPayment no frontend SHALL refletir o downPayment introduzido

**Independent Test**: Abrir Network tab → editar downPayment → verificar POST `/api/deals/{id}/calculations` contém `financingAdjustment.downpayment` e não `downpayment` a raiz

---

### P2: QuotationTemplate Apenas para Bareme Change

**User Story**: Como utilizador, quero que ao navegar no financing tab (tab enter, alterar duration, etc.), o sistema não reenvie o bareme a menos que eu o tenha alterado explicitamente.

**Why P2**: Evita "QT Change" desnecessários que resetam contexto e limpam serviços/configurações.

**Acceptance Criteria**:

1. WHEN `refreshOnTabEnter()` é chamado sem alteração de bareme THEN payload NÃO SHALL conter `quotationTemplate`
2. WHEN utilizador seleciona novo bareme no dropdown THEN payload SHALL conter `quotationTemplate` + `quotationTemplateInfos`
3. WHEN `triggerCalculation` é chamado com `deltaPayload` (duration/distance) sem baremePayload THEN payload NÃO SHALL conter `quotationTemplate`

**Independent Test**: Entrar na financing tab → verificar POST não contém `quotationTemplate`; mudar bareme → verificar POST contém `quotationTemplate`

---

## Edge Cases

- WHEN downPayment = 0 (apagar valor) THEN system SHALL enviar `financingAdjustment.downpayment = "0"` para recalcular sem downPayment
- WHEN deltaPayload contém `downpayment` + `duration` simultaneamente THEN system SHALL extrair `downpayment` para `financingAdjustment` e manter `duration` no payload a raiz
- WHEN `attachFinancialInputs` chamado com `option.deposit = null` THEN system SHALL NÃO incluir `downpayment` no `financingAdjustment`

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
|---------------|-------|-------|--------|
| MMH1483-01 | P1: DownPayment calc | Design | Pending |
| MMH1483-02 | P1: No root downpayment | Design | Pending |
| MMH1483-03 | P1: No QT for normal calc | Design | Pending |
| MMH1483-04 | P2: QT only for bareme change | Design | Pending |

**Status values:** Pending → In Design → In Tasks → Implementing → Verified

**Coverage:** 4 total, 0 mapped to tasks, 4 unmapped ⚠️

---

## Success Criteria

- [ ] Network tab mostra `financingAdjustment.downpayment` no POST (nunca `downpayment` a raiz)
- [ ] Monthly payment ajusta-se após introduzir downPayment
- [ ] Tab enter não envia `quotationTemplate`
- [ ] Mudança de bareme envia `quotationTemplate` corretamente
- [ ] Asset tab continua a funcionar sem regressão
