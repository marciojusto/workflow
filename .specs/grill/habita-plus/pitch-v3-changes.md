# Alterações ao Pitch V3 — pós-grilling (2026-07-30)

Sessão grill-with-docs: 14 decisões em 6 rondas. Este ficheiro lista as alterações necessárias ao `habita-plus-pitch-v3.html`, secção a secção. Aplicável pela Zapia ou manualmente.

## 1. Hero / Posicionamento
- [ ] Acrescentar posicionamento meta-search: "o Kayak do arrendamento medium-term" — agregamos, pontuamos e ligamos à fonte; não republicamos anúncios.
- [ ] Ajustar promessa do fairness score: de "score em cada listing" para "score honesto de preço justo — ou a verdade quando não há dados suficientes".

## 2. Problema
- [ ] NOVA SUB-SECÇÃO: Concorrência. Spotahome, HousingAnywhere, Flatio e Uniplaces já operam MTR em Lisboa/Porto — são marketplaces com inventário próprio e comissões. Diferenciação Habita+: meta-search agregador + pricing intelligence + PT-first, sem gatekeeping de contacto.

## 3. Fase 1 — MVP
- [ ] NOVO PASSO 0 (antes de tudo): Spike de dados (1–3 dias, sem código de produto) — go/no-go da hipótese MTR + JSON Schema derivado dos dados reais. Ver spike-data-validation.md.
- [ ] JSON Schema canónico: passa a derivar do spike (não é o passo imediato anterior).
- [ ] Schema: substituir `photos[]` + `description` persistidos por modelo híbrido (metadata derivada + hotlink + deep link). ADR-001.
- [ ] Modelo de dados: `Property` agrega N `Listing` (dedup não-destrutivo). ADR-001.
- [ ] MTR: `MtrClassification` tri-estado DECLARED/INFERRED/UNKNOWN com confiança. ADR-001.
- [ ] Vector DB: considerar pgvector na Fase 1 (Milvus quando >1M embeddings); corrigir sizing: Milvus Standalone não cabe na mesma VM CX22 4GB com Postgres+Redis+JVM.
- [ ] Frontend: SSR/prerender OBRIGATÓRIO (não opcional) — SEO programático é o canal de aquisição principal.
- [ ] Remover `raw_scrape_logs` persistentes → só payloads de erro, TTL 30d. ADR-002.

## 4. Fase 2 — Growth
- [ ] NOVO: SearchPass one-off ~€14,90/30 dias ao lado da subscrição Pro. ADR-005.
- [ ] NOVO: MarketReport mensal gratuito (antecipado da Fase 3) — SEO + lead-gen B2B. ADR-005.
- [ ] Alertas: 3 eventos (PropertyCreated, ListingCreated em property conhecida, PriceChanged); Free=threshold absoluto, Pro=relativo à mediana. ADR-004.
- [ ] Fairness score: ComparisonPopulation hierárquica por MtrClass + MonthlyEquivalentPrice + cold start honesto. ADR-003.
- [ ] Agente autónomo de contacto: marcar como risco de viabilidade (sem API de mensagens nas fontes; GDPR em contacto automatizado a senhorios). Reavaliar na Fase 3.

## 5. Fase 3 — Scale
- [ ] B2B chega com funil já construído (MarketReport da Fase 2).
- [ ] Domínio B2B usa `Agent`/`Consultant` humano sem colisão (módulo IA renomeado). ADR-006.

## 6. Stack
- [ ] Módulo `agent` → `intelligence`. ADR-006.
- [ ] Score persiste em read-model `intelligence.fairness_scores` via `FairnessScorePort`. ADR-006.

## 7. Arquitetura (secção técnica)
- [ ] Diagrama: renomear módulo; adicionar Property/Listings; eventos canónicos: ListingNormalizedEvent, ListingPriceChangedEvent, ListingRemovedEvent, ScoutSearchedEvent.
- [ ] Ownership: PriceHistory→listing; Geocoding→listing; EntitlementPort→billing.

## 8. Preços
- [ ] Acrescentar SearchPass à tabela B2C.
- [ ] Corrigir projeções MRR/MAU: com conversão 2–5%, €10–25k MRR exige ~50k+ MAU B2C OU ~30–80 clientes B2B — explicitar a mistura.
- [ ] Custos: corrigir linha Milvus/compute do MVP (sizing realista: CX32 ou pgvector).

## 9. Roadmap
- [ ] Nova ordem: Spike de dados → JSON Schema → Skeleton → Scout Agent spike.
- [ ] Fase 2 inclui MarketReport + SearchPass.

## 10. NOVA SECÇÃO: Riscos
- [ ] Legal/ToS: scraping de fontes hostis; mitigação = modelo referrer (ADR-001/002), sem republicação de conteúdo.
- [ ] Dependência de actors Apify de terceiros; plano B por fonte.
- [ ] Cobertura MTR real desconhecida → spike antes de código.
- [ ] Concorrência estabelecida (ver secção Problema).
- [ ] Churn estrutural B2C → SearchPass + relatórios (ADR-005).
