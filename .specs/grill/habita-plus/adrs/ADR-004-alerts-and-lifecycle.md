# ADR-004: Semântica de Alertas e Ciclo de Vida da Property

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (ronda 3)

## Contexto

Com `Property`+`Listing` (ADR-001), os alertas tornam-se diferencial competitivo real — mas o pitch tratava-os como feature menor ("2 alertas no free"). Além disso, o pitch não definia o destino de um imóvel quando todos os seus anúncios desaparecem, desperdiçando o ativo de dados longitudinal (base do B2B da Fase 3).

## Decisões

### 1. Três eventos de alerta
- `PropertyCreated`: imóvel novo que corresponde aos critérios.
- `ListingCreated` em Property já conhecida: "esta casa apareceu no OLX €120 mais barata" — o alerta que agregadores ingénuos (sem dedup consciente) não conseguem dar.
- `PriceChanged`: descida abaixo do threshold configurado.
Utilizador escolhe que eventos cada alerta escuta.

### 2. Thresholds por tier (strategies do Alert)
- Free: `AbsoluteThreshold` — "avisar se T2 em Lisboa < €1.200".
- Pro: `RelativeThreshold` — "avisar se aparecer 15%+ abaixo da mediana móvel da ComparisonPopulation" (o "alerta IA" do pitch).

### 3. Lifecycle da Property: graveyard + reativação
- `ACTIVE → DELISTED` quando o último listing desaparece (evento `ListingRemovedEvent`).
- Property e histórico de preços PRESERVADOS: ativo de dados (TimeOnMarket, turnover por zona, sazonalidade) para relatórios e B2B.
- Se reaparecer no mercado, o matching liga o novo listing à Property existente → `REACTIVATED` — sinal MTR valioso (taxa de rotação).
- GDPR: contactos de anunciante (dados pessoais) purgados quando o listing desaparece; `DELETE /api/v1/me` remove dados do utilizador (alerts, favorites, drafts) e nunca toca em Properties/Listings.

## Consequências

### Positivas
- Alerta multi-fonte é diferencial defensável face a Spotahome/HousingAnywhere.
- Threshold relativo justifica o upgrade Pro com valor real.
- Dados longitudinais acumulam desde o dia 1 sem custo adicional.

### Negativas / Custos
- Deteção de delisting exige reconciliação por fonte (listing ausente em N scrapes consecutivos → removed).
- Reativação depende da qualidade do matching (ADR-002).
- Crescimento contínuo de storage do graveyard (barato: só metadata).

## Alternativas rejeitadas
- Só PropertyCreated + threshold absoluto: perde o alerta multi-fonte.
- Só ListingCreated sem dedup: 3 notificações da mesma casa = spam, alertas descartados em semanas.
- Só threshold relativo: confunde ("o preço subiu mas disparou porque a mediana subiu mais") e colapsa em cold start.
- Soft delete sem reativação ou hard delete: destrói o histórico longitudinal e o sinal de turnover.
