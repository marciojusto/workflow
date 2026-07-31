# Spike de Validação de Dados — Habita+ (Go/No-Go)

- Status: Especificado (não executado)
- Data: 2026-07-30
- Duração estimada: 1–3 dias
- Custo: $5 créditos Apify (plano pessoal)
- Código: NENHUM código de produto. Consola Apify + scripts Python descartáveis.

## Objetivo

Validar ou matar a hipótese central do negócio: **existe oferta Medium-Term Rental (3–12 meses) suficiente e detetável nas fontes alvo para sustentar um agregador.** Se a cobertura MTR real for marginal, o Habita+ não tem matéria-prima — e o skeleton Kotlin é irrelevante.

## Hipóteses a testar

1. H1: ≥15% dos listings em Lisboa/Porto têm elegibilidade MTR declarada ou inferível (DECLARED + INFERRED alta confiança).
2. H2: Os actors Apify devolvem campos suficientes para o schema canónico (preço, tipologia, geo, fotos, descrição).
3. H3: As fotos são hotlinkable a partir dos CDNs das fontes (decisão ADR-002).
4. H4: É possível calibrar um MtrPremium preliminar (MTR vs LTR comparáveis).

## Fontes e actors

| Fonte | Actor Apify | Notas |
|---|---|---|
| Idealista | `igolaizola/idealista-scraper` | Validar geo exata e campos de duração |
| Imovirtual | `logiover/imovirtual-pt-scraper-portugal-real-estate` | Validar cobertura fora de Lisboa |
| OLX | `benthepythondev/olx-scraper` | Validar disponibilidade de morada/geo |

## Medições (checklist)

> **Emenda 2026-07-31 (rebalanceamento de orçamento):** os actors são pay-per-result com preços muito diferentes (Idealista $0.50/1k · Imovirtual $1.50/1k · OLX $5.00/1k). Para caber nos $5 do plano Free: amostra completa (≥1.000/cidade) apenas para Idealista + Imovirtual; **OLX reduzido para ~200/cidade** — suficiente para validar geo/morada (H2) e hotlink (H3), mas com confiança estatística reduzida para H1 na fonte OLX. Decisão: Marcio, formato "rebalanceado free".

### 1. Cobertura MTR (H1)
- [ ] Amostra: ≥1.000 listings por cidade (Lisboa, Porto) por fonte.
- [ ] % com duração explícita (DECLARED): campos min_stay / "arrendamento de temporada" / flags de short-stay.
- [ ] % com sinais INFERRED na descrição — keywords: "temporada", "mensal", "mobilado", "estadias curtas", "curta duração", "disponível de X a Y", "sem contrato longo".
- [ ] Distribuição por cidade × fonte × tipologia (T0–T3+).

### 2. Disponibilidade de campos (H2)
- [ ] Por fonte: preço parseável (%), tipologia, área m2, geo (exata/aproximada/ausente), nº de fotos, comprimento da descrição.
- [ ] Campos de disponibilidade: available_from, min_stay_months, max_stay_months — existem? Preenchidos em que %?
- [ ] Airbnb (se testado via actor alternativo): nightly price, monthly discount flag, offset geo (~100–300m).

### 3. Hotlink de fotos (H3)
- [ ] Referrer-policy e resposta dos CDNs: Idealista (img3.idealista.*), OLX, Imovirtual.
- [ ] Teste: <img> sem Referer e com Referer habitaplus → 200 vs 403.
- [ ] Resultado determina se fallback placeholder é exceção ou norma.

### 4. Volume e qualidade
- [ ] Listings novos/dia estimados por cidade (amostras espaçadas 48h).
- [ ] % preços não parseáveis / "preço sob consulta".
- [ ] Taxa de duplicados intra-fonte (título+geo).

### 5. MtrPremium preliminar (H4)
- [ ] Pares comparáveis (mesma zona + tipologia): mediana MTR vs mediana LTR.
- [ ] Fator por cidade; sanity check contra literatura (+20–40%).

## Critérios de Go/No-Go

| Resultado | Decisão |
|---|---|
| Cobertura MTR (DECLARED+INFERRED) ≥15% E campos ≥80% completos | **GO** — derivar JSON Schema dos dados reais e iniciar skeleton |
| Cobertura 8–15% | **GO CONDICIONADO** — alargar keywords INFERRED, testar Airbnb/FB antes do skeleton |
| Cobertura <8% | **NO-GO / PIVOT** — reavaliar tese: posicionar como agregador geral com inteligência de preço, ou focar canal B2B dados |

## Entregáveis

1. `spike-report.md` — resultados das 5 medições + decisão Go/No-Go fundamentada.
2. `listing-schema-v1.json` — JSON Schema canónico derivado dos dados REAIS (campos presentes ≥80% = required; resto optional).
3. Calibração inicial: thresholds de confiança INFERRED + MtrPremium por cidade.

## Método

1. Correr cada actor na consola Apify contra Lisboa/Porto (queries: arrendamento, todas as tipologias).
2. Exportar datasets JSON.
3. Scripts Python descartáveis (pandas) para as medições 1, 2, 4, 5.
4. Teste de hotlink (medição 3) com curl + HTML de teste local.
5. Redigir spike-report.md com decisão.
