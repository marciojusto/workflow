# ADR-005: Modelo de Receita — Subscrição + Passe, e B2B Lead-Gen Antecipado

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (ronda 4)

## Contexto

Dois problemas no modelo do pitch:
1. **Churn estrutural**: a dor (procurar casa 3–12 meses) dura 2–6 semanas. Subscrição mensal num produto de uso único gera fricção no pagamento ("mais uma subscrição para cancelar") e churn com sentimento negativo.
2. **Projeções incoerentes**: €2–5k MRR com 100 MAU implica conversão 20–50%, contradizendo os 2–5% assumidos no próprio pitch. As contas só fecham com B2B — parado na Fase 3 enquanto o graveyard (ADR-004) acumula dados vendáveis sem gerar nada.

## Decisões

### 1. Subscrição + SearchPass
- Pro €9,90/mês (subscrição) + `SearchPass` one-off ~€14,90/30 dias (mesmos entitlements do Pro, expira automaticamente).
- Domínio: `EntitlementGrant { origin: SUBSCRIPTION | PASS, expires_at }`.
- O passe elimina a fricção de cancelamento e captura quem recusa subscrições para dor temporária.
- Medir conversão dos dois caminhos; o perdedor pode ser descontinuado.

### 2. Relatório mensal gratuito antecipado para a Fase 2
- `MarketReport` mensal ("Estado do Arrendamento MTR em PT") gerado por job (LLM + charts) sobre dados do graveyard.
- Publicado no site: SEO programático + lead capture B2B (email gate).
- Dashboard B2B pago mantém-se na Fase 3 — mas chega lá com lista de leads quentes.
- Custo estimado: ~1 semana de trabalho.

### 3. Enforcement de entitlements (derivação)
- Limites Free (20 favoritos, 2 alertas, etc.) enforced pelos módulos de domínio consultando `EntitlementPort` (owned pelo billing).
- Nenhum módulo calcula entitlements por si.

## Consequências

### Positivas
- Pricing alinhado com o ciclo real da dor; menos ressentimento e churn agressivo.
- B2B começa a gerar funil 6–12 meses antes do dashboard.
- Modelo de entitlements único e testável.

### Negativas / Custos
- Duas ofertas para comunicar e medir (complexidade de pricing page).
- Receita do passe não é recorrente — MRR continua a depender da subscrição.
- Relatório mensal exige dados mínimos acumulados (primeiros meses serão magros).

## Alternativas rejeitadas
- Só subscrição (pitch): fricção máxima no momento de pagar; churn com sentimento negativo.
- Só passe one-off: sem narrativa de MRR; dependência de fluxo constante de novos utilizadores.
- Manter B2B totalmente na Fase 3: desperdiça lead-gen e SEO enquanto os dados ficam parados.
- Antecipar dashboard B2B pago para Fase 2: 6+ semanas de trabalho, atrasa Trust/Scout/Stripe que validam o B2C.
