# MMH-1483: Plano de Execução

## 1. Título e Contexto

**Jira Ticket:** MMH-1483  
**Descrição:** Corrigir downPayment no Financing Tab  
**Scope:** Frontend (hyperfront-worktree) — 1 ficheiro, ~25 linhas de lógica nova  
**Backend:** Zero alterações (PayloadBuilder já correto)

---

## 2. Acceptance Criteria a Implementar

| AC | Requisito | Ficheiro | Linhas |
|----|-----------|----------|--------|
| MMH1483-01 | Extrair downpayment do delta → financingAdjustment | `financing.actions.ts` | ~8 |
| MMH1483-02 | Não enviar downpayment a raiz | `financing.actions.ts` | ~3 |
| MMH1483-03 | Não enviar QT para cálculo normal | `financing.actions.ts` | ~5 |
| MMH1483-04 | QT apenas para bareme change | `financing.actions.ts` | ~3 |

---

## 3. Tarefas

### Task 1: Modificar `_buildCalculationPayload` para extrair campos financeiros do delta
**Ficheiro:** `features/financing/stores/financing.actions.ts`  
**Método:** `_buildCalculationPayload` (linha ~2129)

**Alterações:**
1. Após `normalizeDeltaPayload`, iterar `FINANCIAL_DELTA_FIELDS` e extrair para variável `hasFinancialDelta`
2. Remover campos financeiros do `normalizedDeltaPayload`
3. Recalcular `effectiveDeltaPayload` (null se vazio após extração)

**Código (aprox.):**
```typescript
const FINANCIAL_DELTA_FIELDS = ['downpayment', 'tradeInValue'];
let hasFinancialDelta = false;
if (normalizedDeltaPayload) {
  for (const field of FINANCIAL_DELTA_FIELDS) {
    if (field in normalizedDeltaPayload) {
      hasFinancialDelta = true;
      delete normalizedDeltaPayload[field];
    }
  }
}
const effectiveDeltaPayload = normalizedDeltaPayload && Object.keys(normalizedDeltaPayload).length > 0
  ? normalizedDeltaPayload
  : null;
```

**Verification:** Build passa (`npm run build` no hyperfront)

---

### Task 2: Reescrever lógica de `payload` com base no contexto
**Ficheiro:** `features/financing/stores/financing.actions.ts`  
**Método:** `_buildCalculationPayload`

**Alterações:**
1. Se `effectiveDeltaPayload` presente (e não vazio) → payload = delta
2. Se `productConfigurationOnly` ou `feeToggle` → payload = productConfiguration
3. Se `normalizedBaremePayload` presente → payload = quotationTemplate + infos
4. Senão → payload = `{}` (vazio, attach* functions preenchem)

**Código (aprox.):**
```typescript
let payload: Record<string, any>;
if (effectiveDeltaPayload) {
  payload = effectiveDeltaPayload;
} else if (opts.productConfigurationOnly || isFeeToggle) {
  const services = isFeeToggle ? feeAsServicesPayload : effectiveServicesPayload;
  payload = { productConfiguration: buildProductConfigurationPayload(services, productTypeId) };
} else if (normalizedBaremePayload) {
  payload = {
    quotationTemplate: { quotationTemplateId: refreshedOption.bareme },
    quotationTemplateInfos: normalizedBaremePayload
  };
} else {
  payload = {};
}
```

**Verification:** Build passa

---

### Task 3: Modificar `includeDurationDistance` para forçar `attachFinancialInputs`
**Ficheiro:** `features/financing/stores/financing.actions.ts`  
**Método:** `_buildCalculationPayload`

**Alterações:**
1. `hasNonFinancialDelta = effectiveDeltaPayload` (boolean)
2. `includeDurationDistance = !hasNonFinancialDelta && !opts.productConfigurationOnly`
3. `shouldAttachFinancialInputs = includeDurationDistance || hasFinancialDelta`
4. Retornar `{ payload, includeDurationDistance: shouldAttachFinancialInputs }`

**Verification:** Build passa

---

### Task 4: Validação e Regressão
**Ações:**
1. Build hyperfront: `npm run build` → deve passar
2. Verificar que `attachFinancialInputs` ainda é chamado em `calculateFinancing`
3. Verificar que `resolveCalculationPayload` não é chamado quando há `effectiveDeltaPayload`
4. Verificar que nenhum outro código depende de `includeDurationDistance` como boolean simples

---

## 4. Dependências

| Task | Depende de | Independente? |
|------|-----------|---------------|
| Task 1 | Nenhuma | ✅ Sim |
| Task 2 | Task 1 (effectiveDeltaPayload) | ❌ Não |
| Task 3 | Task 2 (payload construído) | ❌ Não |
| Task 4 | Todas as anteriores | ❌ Não |

**Ordem:** Task 1 → Task 2 → Task 3 → Task 4 (sequencial)

---

## 5. Code Principles Adherence

### DRY (Don't Repeat Yourself)
- ✅ Reutiliza `buildFinancingAdjustment` existente — não duplica lógica de construção do adjustment
- ✅ Reutiliza `attachFinancialInputs` — não duplica código de injeção do adjustment no payload

### KISS (Keep It Simple, Stupid)
- ✅ Solução em 1 ficheiro, ~25 linhas
- ✅ Lógica linear: extrair → construir payload → decidir attach
- ✅ Sem estados complexos, sem máquinas de estado

### YAGNI (You Aren't Gonna Need It)
- ✅ Não adiciona feature flags
- ✅ Não cria novos DTOs
- ✅ Não altera backend
- ✅ Não adiciona novos endpoints

### SOLID / SoC (Separation of Concerns)
- ✅ Controller (`OptionEstimns.vue`) não alterado — continua a chamar `sendScalarDelta`
- ✅ Service (`calculateFinancing`) não alterado — continua a orquestrar
- ✅ Repository/API não alterado — backend intacto
- ✅ Lógica de payload isolada em `_buildCalculationPayload` (única responsabilidade: construir payload)

---

## 6. Clean Code Compliance

### Funções <20 linhas
- ✅ `_buildCalculationPayload` atual: ~35 linhas → após refactor: ~45 linhas (mas cada branch <20)
- ✅ Cada branch do `if` é uma decisão simples (<10 linhas)
- ✅ Extração de `effectiveDeltaPayload` é uma linha

### Nomes descritivos
- ✅ `hasFinancialDelta` — boolean, indica se há campos financeiros no delta
- ✅ `effectiveDeltaPayload` — payload delta após remover campos financeiros
- ✅ `shouldAttachFinancialInputs` — boolean, indica se `attachFinancialInputs` deve ser chamado
- ✅ `FINANCIAL_DELTA_FIELDS` — constante, lista de campos financeiros

### Early Return
- ✅ `if (!normalizedDeltaPayload) return` implícito pelo loop for
- ✅ Cada branch do if/else-if retorna payload imediatamente

### Self-Documenting Code
- ✅ `if (effectiveDeltaPayload)` — claro: há delta não-financeiro
- ✅ `if (normalizedBaremePayload)` — claro: há mudança de bareme
- ✅ Sem comentários explicativos necessários (código auto-explicativo)

---

## 7. Testing Strategy

### 7.1. Testes Manuais (Network Tab)

**Test 1: DownPayment blur**
```
Given: Utilizador no financing tab
When: Edita downPayment para 1000€ e perde foco
Then: Network tab mostra POST com financingAdjustment.downpayment = "1000"
And: Não há campo "downpayment" a raiz
And: Não há "quotationTemplate" no payload
```

**Test 2: Tab enter**
```
Given: Utilizador entra na financing tab (SIMULATION mode)
When: refreshOnTabEnter() é chamado
Then: Network tab mostra POST sem "quotationTemplate"
And: Payload contém financingAdjustment com downPayment atual
```

**Test 3: Duration slider**
```
Given: Utilizador no financing tab
When: Altera duration de 36 para 48 meses
Then: Network tab mostra POST com duration: "48" a raiz
And: Não há "financingAdjustment" (não precisa reenviar downPayment)
```

**Test 4: Bareme change**
```
Given: Utilizador no financing tab
When: Seleciona novo bareme no dropdown
Then: Network tab mostra POST com "quotationTemplate"
And: Payload contém "quotationTemplateInfos"
```

**Test 5: Asset tab regressão**
```
Given: Utilizador na asset tab
When: Altera tradeInValue ou ecoBonus
Then: Asset tab continua a funcionar (calculateDeal chamado)
And: Nenhum erro no console
```

### 7.2. Testes Automatizados

**Build Test:**
```bash
# Hyperfront
npm run build  # Deve passar sem erros
```

**Backend Test (regressão):**
```bash
# Deal-bs
./mvnw test  # Deve passar (sem alterações no backend)
```

### 7.3. E2E (Se aplicável)

Não aplicável — change é no payload, não no UI. Validação via Network tab é suficiente.

---

## 8. Riscos e Mitigações

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| `duration`/`distance` renomeados para `term`/`mileage` | Baixa | Alta | `hasProductConfiguration = true` (synthetic services) evita rename |
| `ecoBonus` perdido no financing tab | Baixa | Média | `buildFinancingAdjustment` já inclui ecoBonus do asset store |
| `productConfiguration` existente perdido | Baixa | Alta | Sem QT → `copyNonServiceFieldsFromExistingConfiguration` preserva campos |
| `configOptions` perdidos | Baixa | Alta | Sem QT → configOptions preservados |
| Build hyperfront falha | Baixa | Alta | Testar build antes de commit |

---

## 9. Commits

| Commit | Mensagem |
|--------|----------|
| 1 | `[MMH-1483] Fix: Extract financial delta fields into financingAdjustment` |

---

**Plano criado em:** 2026-07-02  
**Versão:** 1.0  
**Status:** Pending Approval
