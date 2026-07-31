# ADR-003: Fairness Score — População, Preço de Referência e Cold Start

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (ronda 2)

## Contexto

O pitch definia: mediana + IQR em janela 7d por `city + neighborhood + bedrooms`, score `((preço − mediana)/IQR)×25+50`, "score em cada listing". Três falhas:

1. **Maçãs-e-laranjas**: MTR custa tipicamente +20–40% que LTR (mobília, flexibilidade, utilities). Comparar MTR com a mediana global marca MTRs justos como "muito acima" — o score mentiria sistematicamente contra o público-alvo.
2. **Preços incomparáveis entre fontes**: Airbnb nightly + taxas vs. renda mensal sem utilities.
3. **Cold start**: fora de Lisboa/Porto, as células bairro×tipologia terão n<10 durante meses; um score fabricado destrói a confiança que é o próprio valor do produto.

## Decisões

### 1. ComparisonPopulation hierárquica por MtrClass
Fallback com n mínimo:
1. mesma MtrClass + bairro + tipologia (n≥8)
2. mesma MtrClass + cidade + tipologia (n≥15)
3. população LTR × `MtrPremium` (fator calibrado por cidade, ex. ×1,30) com label "estimativa"

Score sempre acompanhado de n e nível de confiança. MtrPremium calibrado no spike de dados e recalibrado periodicamente.

### 2. MonthlyEquivalentPrice (value object, por Listing)
- Airbnb: (nightly×30 × desconto mensal declarado) + taxa de limpeza amortizada pela estadia + service fee.
- Idealista/OLX: renda mensal (+ condomínio se declarado).
- Score calculado POR LISTING contra a população adequada à sua duração; a Property exibe o range min–max dos seus listings.

### 3. Cold start honesto
- Se n insuficiente em todos os níveis: mostrar "Dados insuficientes para score nesta zona" + contexto disponível (mediana da cidade, range observado, n atual).
- Nunca fabricar número com aparência de precisão sobre amostras mínimas.

## Consequências

### Positivas
- Score matematicamente honesto e defensável — o núcleo da marca ("preço justo").
- Comparabilidade correta entre estruturas de preço heterogéneas.
- Fallback explícito evita scores fantasmas em zonas finas.

### Negativas / Custos
- Exige calibração do MtrPremium (spike + recalibração).
- Explicabilidade mais complexa (label + n + nível do fallback).
- "Score em cada listing" do pitch deixa de ser verdade universal — marketing tem de ajustar a promessa.

## Alternativas rejeitadas
- Não segmentar (mediana global do pitch): injusto estrutural contra MTR.
- Segmentar só por duração declarada: população minúscula, fallback constante.
- Preço mínimo ou mediana dos listings da Property: mistura estruturas incomparáveis.
- Score sempre com aviso de "baixa confiança": número com ar de precisão sobre n=3 é pior que nenhum.
- Esconder a secção em cold start: perde o elemento de marca onde o produto devia brilhar.
