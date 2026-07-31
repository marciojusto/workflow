# Glossário — Habita+ (Língua Ubíqua)

Gerado na sessão grill-with-docs de 2026-07-30. Termos em EN (código) com definição PT (domínio).

## Entidades centrais

| Termo | Definição |
|---|---|
| **Property** | Imóvel físico único (geo, tipologia, área). Agrega N Listings. Dono do histórico e lifecycle (ACTIVE/DELISTED/REACTIVATED). |
| **Listing** | Anúncio de uma Property numa fonte (Idealista, OLX, Airbnb…). Tem preço, condições e MtrClassification próprios. |
| **Source** | Fonte de anúncios agregada via Apify (Idealista, Imovirtual, OLX, Airbnb, FB Marketplace). |

## Classificação MTR

| Termo | Definição |
|---|---|
| **MtrClassification** | Elegibilidade do Listing para arrendamento 3–12 meses: `DECLARED` (fonte explícita), `INFERRED` (LLM sobre descrição, com confiança), `UNKNOWN`. |
| **MTR (Medium-Term Rental)** | Arrendamento de 3 a 12 meses — o gap de mercado alvo do Habita+. |

## Pricing & Scoring

| Termo | Definição |
|---|---|
| **MonthlyEquivalentPrice** | Value object: preço mensal normalizado por fonte. Airbnb = (nightly×30 × desconto mensal) + taxas amortizadas; LTR = renda + condomínio. |
| **ComparisonPopulation** | Conjunto de listings usado para mediana/IQR, segmentado por MtrClass, com fallback hierárquico (bairro→cidade→LTR ajustado). |
| **MtrPremium** | Fator de ajuste MTR↔LTR calibrado por cidade (ex. ×1,30), usado no nível 3 do fallback. Label "estimativa". |
| **FairnessScore** | Score 0–100 + label, calculado por Listing contra a sua ComparisonPopulation. Sempre com n e confiança. |
| **FairnessScorePort** | Interface pública do módulo intelligence para consulta de scores (read-model `fairness_scores`). |
| **TrustSignal** | Sinal de fraude associado a um Listing (nunca à Property). A Property herda o pior badge dos listings ativos. |

## Matching & Ingestão

| Termo | Definição |
|---|---|
| **GrayQueue** | Fila de revisão manual de matches Listing→Property na zona cinzenta do threshold. |
| **RawErrorPayload** | Payload que falhou parsing, retido 30 dias para debug de adapters. Única forma de raw data persistida. |
| **normalizer_version** | Versão das regras do Normalizer registada em cada Listing; mudança de regras implica re-scrape, não reprocessamento. |

## Alertas & Lifecycle

| Termo | Definição |
|---|---|
| **AlertEvent** | Evento que dispara notificação: `PropertyCreated`, `ListingCreated` (em Property conhecida), `PriceChanged`. |
| **AbsoluteThreshold** | Estratégia de alerta Free: preço abaixo de valor fixo definido pelo utilizador. |
| **RelativeThreshold** | Estratégia de alerta Pro: desvio percentual face à mediana móvel da ComparisonPopulation ("alerta IA"). |
| **Reactivation** | Property DELISTED que volta ao mercado; sinal de turnover MTR. |
| **TimeOnMarket** | Dias entre ACTIVE e DELISTED de uma Property. Métrica base de relatórios e B2B. |

## Billing

| Termo | Definição |
|---|---|
| **EntitlementGrant** | Concessão de feature flags ao utilizador: `{ origin: SUBSCRIPTION \| PASS, expires_at }`. |
| **SearchPass** | Passe one-off de 30 dias com os entitlements do Pro. Expira automaticamente. |
| **EntitlementPort** | Interface owned pelo billing para enforcement de limites pelos módulos de domínio. |
| **MarketReport** | Relatório mensal gratuito gerado sobre dados do graveyard (LLM + charts). SEO + lead-gen B2B. Fase 2. |

## Arquitetura

| Termo | Definição |
|---|---|
| **IntelligenceModule** | Módulo Spring Modulith com os serviços de IA/scoring (Scout, Trust, Pricing, Neighborhood). Ex-`agent`. |
| **SearchCriteria** | Value object único de critérios de busca, partilhado por busca manual, Scout Agent e alertas. |
