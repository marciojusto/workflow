# Spike de Validação de Dados — Relatório Preliminar (Dia 1)

- Data: 2026-07-31
- Runs executados: 6 (3 fontes × 2 cidades)
- Custo real: $0.00 (plano Free Apify, créditos intactos)
- Status: Preliminar — aguarda amostra D+2 para volume/dia (medição 4)

---

## H1: Cobertura MTR (DECLARED + INFERRED)

| Fonte | Cidade | n | DECLARED | INFERRED | Total MTR % |
|---|---|---|---|---|---|
| Idealista | Lisboa | 1000 | 0 | 238 | **23.8%** |
| Idealista | Porto | 1000 | 0 | 206 | **20.6%** |
| Imovirtual | Lisboa | 365 | 0 | 34 | **9.3%** |
| Imovirtual | Porto | 365 | 1 | 20 | **5.5%** |
| OLX | Lisboa | 100 | 0 | 29 | **29.0%** |
| OLX | Porto | 100 | 0 | 40 | **40.0%** |

**Achado crítico:** sinal DECLARED é **quase zero** em todas as fontes. O campo `rentalTypes` do actor do Idealista não aparece no output real (ou está vazio). A única exceção é 1 item em Imovirtual-Porto com `monthlyRent` preenchido (interpretado como DECLARED).

**Achado surpreendente:** OLX tem % MTR INFERRED mais alta (29–40%) do que Idealista (21–24%) e Imovirtual (6–9%). Mas: amostra OLX é pequena (n=100 por cidade, margem ±8.8% a 95% CI), enquanto Idealista tem n=1,000 (margem ±2.7%). O resultado de OLX pode ser viés de amostra.

**Palavras-chave que dispararam INFERRED:** "mobilado" (dominante nos títulos OLX), "temporada", "mensal", "curta duração", "disponível de X a Y".

### ⚠️ Risco para H1
O threshold do spike é **≥15% DECLARED + INFERRED**. A taxa total combinada é ~19.4% (567/2930), mas é **100% INFERRED via keywords em títulos/descrições**. Isto tem dois problemas:
1. **Falsos positivos:** "mobilado" aparece em arrendamentos de longa duração também. A keyword "mobilado" sozinha não é suficiente para inferir MTR — precisa de contexto (ex.: "mobilado para estadias curtas", "arrendamento temporário").
2. **Precisão do sinal:** sem validação manual de uma amostra dos 567 INFERRED, não sabemos a precision/recall do classificador. O spike mede recall (quantos MTR conseguimos detetar), mas se a precision for baixa, o catálogo fica poluído.

**Decisão:** Refinar keywords no Dia 3 (excluir "mobilado" isolado, exigir co-ocorrência com "temporada"/"curta duração"/"mensal" + duração) e validar ~50 items manualmente para estimar precision.

---

## H2: Disponibilidade de campos (%)

| Campo | Idealista | Imovirtual | OLX |
|---|---|---|---|
| price | 100.0% | 99.9% | 100.0% |
| tipologia | 100.0% | 100.0% | 0.0% |
| geo (lat/lon ou district) | 100.0% | 100.0% | 0.0% |
| fotos | 99.5% | 98.6% | 99.0% |
| descrição (>20 chars) | 99.1% | **0.0%** | 100.0% |
| **all_fields** | **98.8%** | **0.0%** | **0.0%** |

**Achados:**
- **Idealista** é a fonte mais completa (98.8% all_fields). Schema quase canónico.
- **Imovirtual** tem excelentes campos factuais (price, tipologia, geo, fotos) mas **0% de descrição integral**. O actor devolve `shortDescription` e `title`, mas não `description` (provavelmente não está no `__NEXT_DATA__` ou o actor não o extrai). Isto significa: MTR INFERRED para Imovirtual depende só de `title` + `shortDescription` — precisão limitada.
- **OLX** tem preço e descrição, mas **0% tipologia estruturada** (rooms está dentro de `attributes` dict, não parseado) e **0% geo estruturado** (`district` é None na maioria dos items). A geo vem só no `city` (município, não bairro).

### Conclusão H2
≥80% de completude para o schema canónico: **apenas Idealista** (98.8%). Imovirtual e OLX precisam de normalização adicional. O `listing-schema-v1.json` deve refletir campos por fonte, com required/unqualified por origem.

---

## H3: Hotlink de fotos

| Fonte | sem Referer | com Referer habitaplus.pt |
|---|---|---|
| Idealista (img4.idealista.pt) | 301 (redirect) | 301 (redirect) |
| Imovirtual (apollo.olxcdn.com) | **200** | **200** |
| OLX (apollo.olxcdn.com) | **200** | **200** |

**Veredito:** hotlink viável para todas as fontes. Nenhum 403. Idealista redireciona (normal para CDN de imagens); OLX e Imovirtual respondem 200 direto. O ADR-002 (content retention via hotlink) é tecnicamente válido.

---

## H4: Volume e qualidade (preliminar)

| Fonte | Lisboa | Porto | Total |
|---|---|---|---|
| Idealista | 1000 | 1000 | 2000 |
| Imovirtual | 365 | 365 | 730 |
| OLX | 100 | 100 | 200 |
| **Total** | **1465** | **1465** | **2930** |

**Achados:**
- Idealista atingiu o cap de 1.000/cidade — inventário suficiente.
- Imovirtual **não chegou a 1.000** — cap de inventário em ~365/cidade na altura do scrape. Isto é um dado real para a estimativa de volume do spike.
- OLX limitado a 100/cidade por custo (rebalanceamento free).
- % preços não parseáveis: 0% nas 3 fontes (todos os preços são numéricos).
- "Preço sob consulta": não observado nas amostras (mas pode existir em filtros não capturados).
- Duplicados intra-fonte: não medidos ainda (requer diff por URL/título+geo).
- **Novos listings/dia:** impossível medir no Dia 1 — requer amostra D+2 (48h spacing).

---

## Custos reais medidos

| Fonte | Run | CUs | chargeUsd |
|---|---|---|---|
| Idealista-Lisboa | 75.8s | 0.0026 | $0.00 |
| Idealista-Porto | 83.8s | 0.0029 | $0.00 |
| Imovirtual-Lisboa | 33.4s | 0.0093 | $0.00 |
| Imovirtual-Porto | 67.7s | 0.0188 | $0.00 |
| OLX-Lisboa | 8.3s | 0.0092 | $0.00 |
| OLX-Porto | 8.3s | 0.0093 | $0.00 |
| **Total** | | | **$0.00** |

Os $5 de crédito do plano Free estão **intactos**. Os actors pay-per-result (Idealista $0.50/1k, Imovirtual $1.50/1k, OLX $5.00/1k) não foram faturados nesta execução — possível consumo do Free tier incluído ou billing em lote.

---

## listing-schema-v1.json (preliminar)

Campos presentes ≥80% no amostra combinada (n=2930):
- **required:** price, tipologia, geo (lat/lon ou district)
- **recommended:** photos, description
- **optional:** tudo o resto

Nota: schema valida-se como final no Dia 3 após 2ª amostra e validação de keywords.

---

## Próximos passos (Dia 3)

1. Colher 2ª amostra (~48h depois da 1ª) para medição 4 (novos listings/dia).
2. Refinar keywords MTR (remover "mobilado" isolado) e validar precision com sample manual de ~50 items.
3. Fechar `listing-schema-v1.json` e `spike-report.md` final com recomendação Go/No-Go.
