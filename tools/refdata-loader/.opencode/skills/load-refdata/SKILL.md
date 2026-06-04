---
name: load-refdata
version: v1.0.0
description: Carrega dados de quotes + credit applications de um salesperson para um MongoDB de referência (refdev ou refasy).
priority: medium
---

# Carregar dados de referência para MongoDB

### Pré-requisitos

- Containers MongoDB a correr: `docker compose -f ~/Development/teamwill/mobilize/workflow/tools/refdata-loader/docker-compose.refdata.yaml up -d`
- Token Okta salvo em `~/.config/refdata-loader/okta-token` (ou `OKTA_TOKEN` env)
- Projecto em: `~/Development/teamwill/mobilize/workflow/tools/refdata-loader`

### Convensão: guardar em `data/`

Coloca os JSONs em `data/` dentro do projecto:

```
workflow/tools/refdata-loader/data/
├── credit-applications.json
├── quotes.json
└── contracts.json
```

Depois o comando fica simples:

```bash
npx tsx src/index.ts load-files --target refdev --credit-apps data/credit-applications.json --quotes data/quotes.json
```

### Fluxo principal (load-files)

O utilizador fornece 3 ficheiros JSON (arrays de objetos):

| Ficheiro | Exemplo | Obrigatório |
|---|---|---|
| `credit-applications.json` | Array de respostas da API credit-retail | Sim |
| `quotes.json` | Array de respostas da API quotation | Sim |
| `contracts.json` | Array de respostas da API contracts | Opcional |

```bash
cd ~/Development/teamwill/mobilize/workflow/tools/refdata-loader
npx tsx src/index.ts load-files \
  --target refdev \
  --credit-apps ./credit-applications.json \
  --quotes ./quotes.json \
  --contracts ./contracts.json \
  --dry-run
```

Remove `--dry-run` para escrever na MongoDB.

### Relação entre os ficheiros

- Cada `credit-application` tem um `salesQuote.salesQuoteId` que liga ao `salesQuoteId` no array quotes
- Cada `contract` tem um `creditApplicationId` que liga ao `creditApplicationId` da credit-app
- Se faltar a quote correspondente a uma credit-app, essa linha é skipped

### Estrutura esperada dos JSONs

**credit-applications.json** — array de objetos, cada um com:
```json
{
  "creditApplicationId": "CAPP-123",
  "salesQuote": { "salesQuoteId": "QSQ-456" },
  "status": { "enumId": "...", "enumGroupId": "..." },
  "decision": { "enumId": "...", "enumGroupId": "..." }
}
```

**quotes.json** — array de objetos, cada um com:
```json
{
  "salesQuoteId": "QSQ-456",
  "reference": "QSQ-456",
  "carConfiguration": { ... },
  "customer": { ... },
  "brokerContactRepresentation": { ... },
  "quoteStatus": { ... }
}
```

### Outros comandos auxiliares

```bash
# Obter token (Keycloak password grant)
npx tsx src/index.ts login --username twam1 --password 123456Cc

# Quem sou eu (broker do token atual)
npx tsx src/index.ts whoami --target refdev

# Listar brokers
npx tsx src/index.ts sellers --target refdev
```

### Em caso de erro

| Erro | Causa | Solução |
|---|---|---|
| Token not found | `okta-token` ausente | `login` ou Okta PKCE via IntelliJ |
| 401 Unauthorized | Token expirado | Renovar com `login` |
| MongoDB connection refused | Container down | `docker compose -f .../docker-compose.refdata.yaml up -d` |
| File not found | Path errado | Verificar caminho do JSON |
