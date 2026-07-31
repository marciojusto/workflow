# ADR-001: Modelo de Identidade do Listing

- Status: Accepted
- Data: 2026-07-30
- Sessão: grill-with-docs / grilling Habita+ (rondas 1 e 1.5)
- Decisores: Marcio Justo + assistente (grilling)

## Contexto

O pitch V3 definia um `Listing` canónico full-content: fotos + descrição integral persistidas na base de dados. Três problemas forçaram revisão:

1. **Exposição legal**: persistir e republicar conteúdo integral (fotos, descrições) de Idealista/OLX/Airbnb/FB Marketplace é reprodução de conteúdo protegido — database right (Diretiva 96/9/CE), ToS das fontes, e GDPR no caso do FB Marketplace (dados pessoais de anunciantes).
2. **Deduplicação destrutiva**: o pitch previa merge de duplicados, o que destrói o sinal multi-fonte (a mesma casa mais barata noutra fonte é um diferencial).
3. **MTR indefinido**: a proposta de valor é Medium-Term Rental (3–12 meses), mas as fontes raramente declaram `min_stay` — o domínio precisava de representar esta incerteza honestamente.

## Decisões

### 1. Modelo híbrido de conteúdo
- Ingestão processa TUDO (descrição alimenta embeddings, classificação MTR e Trust Agent).
- Persiste-se apenas metadata derivada: campos factuais (título, preço, localização, tipologia, área), scores, classificações, embeddings.
- NÃO se persiste descrição integral nem fotos.
- UI mostra resumo próprio (gerado) + fotos via hotlink da fonte + deep link — posicionamento meta-search ("Kayak do MTR").

### 2. Property agrega Listing
- `Property` = imóvel físico único (geo, tipologia, área). Dono do histórico e do contexto de preço.
- `Listing` = um anúncio de uma Property numa fonte, com preço e condições próprias.
- Deduplicação NÃO destrutiva: 1 Property → N Listings.
- Preserva o diferencial "também no Airbnb / €120 mais barato no OLX".

### 3. Classificação MTR tri-estado
- `MtrClassification`: `DECLARED` (fonte explícita) | `INFERRED` (LLM sobre descrição, com score de confiança) | `UNKNOWN`.
- Filtro default de catálogo: DECLARED + INFERRED acima de threshold de confiança (threshold calibrado no spike de dados).
- O utilizador pode alargar o filtro para incluir UNKNOWN.

## Consequências

### Positivas
- Exposição legal mínima: sem republicação de conteúdo protegido.
- Alertas multi-fonte (ADR-004) tornam-se possíveis.
- Honestidade sobre incerteza MTR é defensável perante utilizadores e fontes.

### Negativas / Custos
- UI depende de hotlink de fotos (mitigado no ADR-002).
- Sem descrição persistida, reprocessamento exige re-scrape (mitigado por `normalizer_version`, ADR-002).
- Modelo de dados mais rico (duas entidades + matching) que o schema original do pitch.

## Alternativas rejeitadas
- Meta-search puro (sem processamento de descrição): matava search semântico e classificação MTR.
- Full-content (schema do pitch): exposição legal máxima.
- Merge destrutivo de duplicados: perdia sinal multi-fonte e histórico por fonte.
- MTR binário rígido: catálogo nasceria quase vazio.
