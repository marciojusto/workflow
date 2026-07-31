# ADR-002: Estratégia de Conteúdo, Fotos e Retenção

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (ronda 1.5)

## Contexto

Decidido o modelo híbrido (ADR-001), restavam três problemas concretos:
1. CDNs das fontes podem bloquear hotlinking de fotos (referrer-check) — a ficha ficaria vazia.
2. O pitch previa `raw_scrape_logs` persistidos para debug — contradiz o modelo híbrido e, no FB Marketplace, retém dados pessoais (GDPR).
3. Airbnb ofusca geo (~100–300m de offset) e OLX raramente publica morada exata — matching Listing→Property agressivo fundiria imóveis diferentes.

## Decisões

### 1. Fotos: hotlink + fallback gracioso
- Tentar hotlink direto do CDN da fonte.
- Se bloqueado: imagem placeholder genérica (mantém layout) + contador + link "Ver N fotos no {Fonte} →".
- Zero cópia de imagens em infraestrutura própria.
- Validação técnica (referrer-policy dos 3 CDNs) incluída no spike de dados.

### 2. Retenção: só payloads de erro
- Não existem `raw_scrape_logs` persistentes.
- Guardam-se apenas payloads que falharam parsing (debug de adapters), com TTL de 30 dias e purge automático.
- Cada Listing carrega `normalizer_version`; quando as regras mudam, re-scrape substitui reprocessamento (custo marginal via Apify).

### 3. Matching conservador + fila cinzenta
- Score composto: geo ponderado por fonte (Airbnb: raio 300m; Idealista/OLX: 50m) + tipologia + área ±10% + similaridade título/descrição.
- Acima do threshold → match automático; zona cinzenta → `GrayQueue` (revisão manual); abaixo → Property nova.
- Princípio: preferir falso negativo (duplicado visível) a falso positivo (imóveis fundidos corrompem medianas).

## Consequências

### Positivas
- Coerência total com o modelo híbrido; exposição GDPR limitada e auditável.
- UX nunca "parte" por bloqueio de CDN.
- Fairness score protegido de merges errados.

### Negativas / Custos
- Debug de normalização limitado a payloads de erro recentes.
- `GrayQueue` exige operação manual contínua (volume a medir no spike).
- Possível degradação visual se os CDNs bloquearem hotlink em massa.

## Alternativas rejeitadas
- Proxy de thumbnails com cache 72h: reprodução temporária de obra protegida — risco que o modelo híbrido visa evitar.
- Raw logs indefinidos ou com purge 7–14d: retenção de conteúdo integral sem necessidade proporcional.
- Matching 100% automático: erros silenciosos corrompem scores.
- Match só por morada exata: taxa de match real <30% (Airbnb/OLX), matando o diferencial multi-fonte.
