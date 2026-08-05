# ADR-007: Estratégia de Comunicação Inter-Módulos

- Status: Accepted
- Data: 2026-08-04
- Sessão: Implementação HP-001/HP-002

## Contexto

O Habita+ é construído como um monólito modular (Spring Modulith) com módulos `listing`, `intelligence`, `search`, `alert`, `billing`, e futuramente `b2b`. Estes módulos precisam de comunicar entre si.

A questão surgiu durante a implementação de HP-002 (ingestion module): qual protocolo usar para comunicação entre módulos — REST, gRPC, ou chamadas in-process?

## Decisão

**Fase atual (monólito):** comunicação **in-process** via:
- **Eventos assíncronos** (`ApplicationEventPublisher`) — ex.: `ListingNormalizedEvent` do `listing` para `intelligence`
- **Ports síncronos** (interfaces) — ex.: `FairnessScorePort` do `intelligence` para `search`

**Futuro (microserviços):** gRPC para comunicação interna entre serviços; REST para API pública e integração com terceiros.

## Alternativas Consideradas

| Alternativa | Porquê rejeitada |
|---|---|
| REST entre módulos | Overhead desnecessário no monólito; serialização JSON desnecessária; N+1 potencial via HTTP |
| gRPC entre módulos | Complexidade desnecessária no monólito; requer code generation; debugging mais difícil; browsers não suportam nativamente |
| Mensageria (Kafka/RabbitMQ) | Overkill para comunicação síncrona; adiciona infraestrutura; eventual consistency não justificada para o MVP |
| **In-process (eventos + ports)** | **Escolhida** — zero overhead, type-safe, debugging simples, alinhado com Spring Modulith |

## Consequências

### Positivas
- **Performance máxima:** chamadas de método Java/Kotlin na mesma JVM — zero serialização, zero latência de rede
- **Type safety:** compilador garante compatibilidade de interfaces
- **Debugging simples:** stack traces nativos, sem protocolo de rede
- **Alinhamento com Spring Modulith:** `ModulithBoundariesTest` valida que módulos não quebram fronteiras
- **Migração futura para microserviços:** eventos e ports são contratos estáveis; quando extraíres para gRPC, os contratos já estão definidos

### Negativas / Custos
- **Acoplamento temporal no monólito:** módulos na mesma JVM; se um módulo falhar, afeta o outro (mitigado por eventos assíncronos onde apropriado)
- **Refator futura:** quando extraíres para microserviços, precisas de substituir chamadas in-process por gRPC — mas os contratos (ports/eventos) já existem
- **N+1 em LAZY associations:** risco real (mitigado com `@BatchSize(50)` no `Property`, como documentado em HP-001)

## Regras de Comunicação

| Cenário | Protocolo | Justificação |
|---|---|---|
| Módulo → módulo (monólito) | In-process (evento/port) | Zero overhead, type-safe |
| API pública / frontend | REST | Compatibilidade universal, caching HTTP |
| Integração com terceiros (Apify) | REST | É o que os terceiros oferecem |
| Microserviços internos (futuro) | gRPC | Performance, streaming, contratos fortes |
| Webhooks / SSE | REST/SSE | Browser compatibility |

## Referências

- ADR-001: Listing Identity Model (posicionamento meta-search)
- ADR-006: Bounded Contexts (renomeação `agent` → `intelligence`, ports, eventos canónicos)
- HP-001: Listing Domain Model + Property Aggregate
- HP-002: Ingestion Module (Apify Client + Normalizers)
