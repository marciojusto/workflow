---
name: convert-conversation
version: v1.0.0
description: "Converts raw .txt conversation files into structured .md wiki notes. Can be invoked standalone or by wiki-keeper for automatic detection."
---

## Inputs
- `filepath` (optional) — specific .txt file to convert
- If omitted: scan `~/Development/teamwill/mobilize/workflow/karpathy/wiki/conversations/` for `.txt` files and prompt user to pick one

## Output
- `converted_path` — path of the generated .md file
- `title` — extracted title

## Process

### 1. Resolve target file
- If `filepath` provided and exists → use it
- If not provided: list all `.txt` files in `conversations/` directory, show them numbered, and ask user which one to convert

### 2. Read the .txt content
- Read the full raw text

### 3. Extract metadata
Analyse the content and extract:
- **Tema/assunto** — first meaningful line or subject
- **Data** — try to find a date in the text; if not found, use file modification date
- **Participantes** — names of people involved; ask user if unclear
- **Tags de domínio** — based on content keywords:
  - `#conversa` always
  - `#okta` (auth, login, Okta)
  - `#party` (customer, driver, fleet)
  - `#offer` (quotation, pricing, proposals)
  - `#stipulations` (contract terms, conditions)
  - `#contract` (contracts, agreements)
  - `#delivery` (vehicle delivery)
  - `#catalog` (vehicle catalog)
  - `#general` (no specific domain)
  - `#hyperfront` or `#deal-bs` (technical discussions)
  - Ask user if ambiguous or if unsure about any metadata

### 4. Create .md file
Generate a structured markdown file in the same directory:

```markdown
# {tema} - {data}

- **Participantes**: {nomes}
- **Data**: {data}
- **Tags**: {tags}

---

## Resumo

{breve parágrafo resumindo a conversa}

## Notas

- {ponto relevante 1}
- {ponto relevante 2}

## Decisões / Action Items

- [ ] {pendência 1}
- [x] {decisão tomada}
```

### 5. Delete the .txt file
Remove the original `.txt` after successful conversion.

### 6. Return result
Return `converted_path` and `title` for caller to use.

## Important Rules
- NEVER leave the original .txt behind after conversion
- If metadata extraction is ambiguous, ask user — don't guess
- The .md must be clear and useful for future reference
