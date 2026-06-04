---
name: create-plan
version: v1.0.0
description: Criar plano técnico baseado na user story ou bug fix
---

# Create Plan

## Config
requires_mode: plan

## Inputs
- title
- description
- current_ac
- jira_ticket_id
- current_ac_index
- acceptance_criteria (can be empty for bug tickets)

## Output
- plan
- plan_path

## Instructions
Antes de criar o plano, garante que o CLI está em **plan mode**.

Se o CLI não estiver em plan mode, força a transição para plan mode usando o comando `/plan` ou equivalente do CLI.

Cria um plano técnico detalhado para implementar a current_ac.

**Importante**: Todo código criado (variáveis, funções, comentários, nomes de ficheiros) DEVE estar em inglês.
O texto do plano também deve ser em inglês.

### Handling Bug Tickets
If `acceptance_criteria` is empty or `current_ac` is "Fix the bug described in the ticket description":
- Use the ticket **description** as the main task to fix
- Analyse the description to understand the bug and how to fix it
- Include steps to reproduce and fix the bug

O plano DEVE incluir:
1. **Passos da AC** — Lista todos os passos/subtarefas mencionados na Acceptance Criteria (or description for bugs)
2. **Implementação** — Para cada passo, descreve o que será implementado (ficheiros, componentes, APIs, etc.)
3. **RAG Materials Used** — Lista todos os materiais de RAG disponibilizados que foram utilizados para criar o plano
4. **RAG Materials NOT Used** — Lista os materiais de RAG que NÃO foram utilizados e JUSTIFICATIVA do porquê

Exemplo de estrutura no plano:
```markdown
## Passos da AC
1. "O utilizador pode seleccionar o campo X"
2. "O valor Y é calculado automaticamente"

## Implementação
### Passo 1: Selecção do campo X
- Ficheiro: `src/features/deals/components/DealForm.vue`
- Adicionar componente de select com valores do enum
- Utilizar o composable `useDealFields()`

### Passo 2: Cálculo automático do valor Y
- Criar computed property em `useDealCalculations.ts`
- Fórmula: ...

## RAG Materials Used
- `.workflow/RAG/MMH_1435/Asset Tab V1.xlsx` - Used for understanding vehicle pricing fields
- `.workflow/RAG/sprint_01/requirements.md` - Used for sprint context

## RAG Materials NOT Used
- None - all provided materials were relevant
```

### Leitura de ficheiros Excel
Quando `rag_resources` contém ficheiros Excel (extensão .xlsx), deves ler o conteúdo usando o script `.workflow/scripts/read_excel.py`:

O caminho do ficheiro está disponível em `rag_resources` — exemplo:
```
{ "api_name": "mmh_1435", "spec_path": ".workflow/RAG/MMH_1435", "filename": "Asset Tab V1.xlsx" }
```

Comando:
```bash
python3 .workflow/scripts/read_excel.py "<spec_path>/"
# ou para uma folha específica:
python3 .workflow/scripts/read_excel.py "<spec_path>/" "SheetName"
```

Exemplo:
```bash
python3 .workflow/scripts/read_excel.py ".workflow/RAG/MMH_1435/Asset Tab V1.xlsx"
```

Este script retorna o conteúdo do Excel em formato JSON, listo para ser usado no plano.

## Steps

1. ensure-plan-mode
   - logic:
     - check if current CLI mode is "plan"
     - if not, switch to plan mode using CLI command (e.g., /plan or mode switch)
     - wait for mode confirmation

2. build-plan
   - input: title, description, current_ac
   - logic:
     - analyse current_ac and all context (title, description)
     - create detailed technical plan with small steps
     - include file paths and decisions
     - return plan object

3. save-plan
   - call: mcp.filesystem.write_file
   - input:
     path: "~/Development/teamwill/mobilize/workflow/plans/{jira_ticket_id}_ac{current_ac_index}_plan.md"
     content: plan as markdown document
   - logic:
     - ensure ~/Development/teamwill/mobilize/workflow/plans/ directory exists
     - write markdown file with plan content
     - return plan_path