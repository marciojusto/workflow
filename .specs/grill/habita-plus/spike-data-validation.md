# Spike de Validação de Dados — Habita+ (Go/No-Go)

- Status: Especificado (não executado)
- Data: 2026-07-30
- Duração estimada: 1–3 dias
- Custo: $5 créditos Apify (plano pessoal)
- Código: NENHUM código de produto. Consola Apify + scripts Python descartáveis.

## Objetivo

Validar a hipótese central do negócio sob o MVP **agregador geral + filtro MTR**:
1. **Sobrevivência do agregador:** existe oferta suficiente (campos completos ≥80%, hotlink viável) nas fontes alvo para sustentar um catálogo geral de arrendamento.
2. **Diferenciação MTR:** a oferta MTR (3–12 meses) é detetável e quantificável — suficiente para ser um filtro competitivo, não apenas ruído.

Se H2 (campos) ou H3 (hotlink) falharem, o Habita+ não tem matéria-prima. Se o MTR for apenas residual (<5%), o filtro MTR é um diferencial fraco, mas o agregador geral ainda pode avançar com a intelligence de preço como proposta de valor.

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

## Critérios de Go/No-Go (MVP: agregador geral + filtro MTR)

| Resultado | Decisão |
|---|---|
| Campos ≥80% completos (H2) E hotlink OK (H3) | **GO** — agregador geral viável; derivar JSON Schema e iniciar skeleton |
| MTR cobertura ≥15% (DECLARED+INFERRED com keywords conservadoras) | **GO + MTR como diferencial forte** — filtro MTR é competitivo desde dia 1 |
| MTR cobertura 8–15% | **GO + MTR como diferencial fraco** — agregador geral avança; MTR filter requer LLM para precision aceitável |
| MTR cobertura <8% | **GO (posicionamento revisado)** — agregador geral com intelligence de preço; MTR fica como filtro secundário ou é removido do pitch |
| Campos <80% ou hotlink bloqueado | **NO-GO** — matéria-prima insuficiente para qualquer variante do produto |

## Entregáveis (ajustados ao MVP)

1. `spike-report.md` — resultados das 5 medições + recomendação de MVP.
2. `listing-schema-v1.json` — JSON Schema canónico **por-fonte** derivado dos dados REAIS (campos presentes ≥80% = required; resto optional). Idealista é a fonte primária; Imovirtual e OLX têm schemas reduzidos.
3. Calibração inicial: thresholds de confiança INFERRED + MtrPremium por cidade (para o filtro MTR).
4. `spike-mtr-validation-sample.csv` — 50 items para validação manual de precision do classificador MTR.

## Método

1. Correr cada actor na consola Apify contra Lisboa/Porto (queries: arrendamento, todas as tipologias).
2. Exportar datasets JSON.
3. Scripts Python descartáveis (pandas) para as medições 1, 2, 4, 5.
4. Teste de hotlink (medição 3) com curl + HTML de teste local.
5. Redigir spike-report.md com decisão.


## Emenda 2026-08-03 — Reframing do MVP

Após análise dos dados, o MVP do Habita+ passa a ser **agregador geral de arrendamento com filtro MTR como diferenciador incremental**, e não "MTR-only". Esta alteração impacta os critérios de Go/No-Go: o survival gate é agora a disponibilidade de campos (H2) e hotlink (H3), não a cobertura MTR. A cobertura MTR informa a força do diferencial, mas não mata o projeto se for baixa.
