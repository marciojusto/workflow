# ADR-006: Bounded Contexts — Rename do Módulo IA e Fronteira do Score

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (ronda 5)

## Contexto

Duas falhas no desenho de módulos do pitch (Spring Modulith):
1. **Colisão semântica**: o módulo chama-se `agent` (agentes IA). Na Fase 3 entra o B2B com imobiliárias — e "agente imobiliário" é o ator humano central desse domínio. Dois `Agent` no mesmo codebase, eventos e glossário.
2. **Dependência circular escondida**: o Pricing Analyst vive em `agent` e consome `ListingNormalizedEvent`, mas o pitch não diz onde o score persiste. Se na entidade `Listing` (módulo `listing`), `agent` escreve dentro de `listing` → violação de fronteira. Se `listing` pedir o score sincronamente, cria-se o ciclo listing→agent→listing.

## Decisões

### 1. Rename: `agent` → `intelligence`
- Scout, Trust, Pricing, Neighborhood passam a ser intelligence services.
- `Agent` (consultor imobiliário humano) fica livre para o domínio B2B da Fase 3.
- Custo agora: zero. Na Fase 3: refactor de módulo + eventos + tabelas + docs.

### 2. Score em read-model + Port
- `intelligence` é dono absoluto da sua tabela `fairness_scores` (listing_id, score, label, n, confidence, computed_at) — read-model recalculável.
- Expõe `FairnessScorePort`; a API de busca (listing/web) chama o port in-process para enriquecer respostas.
- `listing` nunca conhece `intelligence`; o fluxo é evento → cálculo → read-model → port.
- `ModulithBoundariesTest` passa sem exceções.

### 3. Derivações de ownership (registadas na sessão)
- `PriceHistory`: capturado por `listing` (dono do scheduler), consumido por `intelligence`.
- Geocoding (Mapbox): infraestrutura de ingestão → `listing`.
- `TrustSignal`: por Listing (fraude é comportamento do anunciante; a Property herda o pior badge dos listings ativos).
- `SearchCriteria`: value object único partilhado por busca manual, Scout e alertas ("guardar busca como alerta" é trivial).
- Eventos canónicos: `ListingNormalizedEvent`, `ListingPriceChangedEvent`, `ListingRemovedEvent`, `ScoutSearchedEvent`.

## Consequências

### Positivas
- Língua ubíqua limpa para o B2B sem refactor tardio.
- Fronteiras Modulith rigorosas; scores recalculáveis sem tocar em listings.
- Ownership de dados sem ambiguidade.

### Negativas / Custos
- Enriquecimento de resposta via port exige cuidado com N+1 (batch fetch por página de resultados).
- Read-model pode divergir temporariamente após recalibragem do MtrPremium (recálculo assíncrono).

## Alternativas rejeitadas
- Manter `agent` e nomear o humano `Consultant`: torce a língua ubíqua do negócio por conveniência técnica.
- Resolver na Fase 3 (YAGNI): poupa 10 minutos agora, paga refactor quando o codebase é grande.
- Evento write-back (`FairnessScoreComputedEvent` → listing persiste): eventual consistency + evento cujo único propósito é escrita cruzada.
- Score síncrono na ingestão: ciclo de dependências + acopla ingestão à disponibilidade do scorer.
