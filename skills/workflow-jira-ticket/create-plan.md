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
5. **Code Principles Adherence** — Para cada princípio, documenta como a implementação proposta o respeita:
   - **DRY**: Identifica código/funções existentes que podem ser reutilizados. Se algo novo for criado, justifica por que não existe equivalente.
   - **KISS**: Propõe a abordagem mais simples que resolve o problema. Evita abstrações desnecessárias, máquinas de estado desnecessárias, ou patterns que a complexidade não justifica.
   - **YAGNI**: Implementa apenas o que a AC pede. Nada de "preparar para o futuro", "deixar extensível", ou código não especificado.
   - **SOLID**: Cada componente/ficheiro tem uma única responsabilidade. Separa UI de lógica. Usa composables para lógica reutilizável.
   - **SoC**: Todas as chamadas API via bsClient (nunca fetch direto em componentes). Dados em Pinia stores. Lógica de negócio em composables ou server/api/.
6. **Clean Code Compliance** — Documenta como o código seguirá boas práticas:
   - **Small Functions**: Funções com no máximo 20 linhas
   - **Descriptive Names**: Nomes descritivos sem abreviações (ex: `user` não `u`, `count` não `cnt`)
   - **Max 3 Parameters**: Usar objeto se mais de 3 parâmetros
   - **Early Return**: Usar guard clauses para reduzir aninhamento
   - **English Only**: Todas as variáveis, funções e comentários em inglês
   - **Readability First**: Código escrito para humanos — claro, legível, sem truques inteligentes
7. **Testing Strategy** — Define a estratégia de testes:
   - **TDD**: Test-Driven Development quando aplicável
   - **Given-When-Then**: Para testes de comportamento
   - **Arrange-Act-Assert**: Para testes unitários
   - **Test Names**: Nomes que descrevem o cenário, não a implementação

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
