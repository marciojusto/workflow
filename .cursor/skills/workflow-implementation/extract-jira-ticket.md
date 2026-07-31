---
name: extract-jira-ticket
version: v1.0.0
description: Extrair user story ou bug info e critérios de aceitação a partir de um ticket do Jira.
---

# Extract Jira Ticket

## Config
retry: 1
on_error: return_empty

## Inputs
- jira_ticket_id

## Output
- title
- description
- acceptance_criteria
- current_ac
- current_ac_index
- total_ac_count
- all_done
- attachments
- links
- linked_issues
- existing_plan
- rag_resources
- changes_detected

## Instructions
Você coletará as informações de uma issue do Jira, verificará alterações desde a última execução e determinará qual AC deve ser implementada a seguir.

Na primeira execução para um ticket, guarda um snapshot do estado actual.
Em execuções subsequentes, compara o estado actual com o snapshot guardado e reporta alterações ao utilizador.

Sua tarefa:
- Extrair o título (summary) da issue
- Extrair a descrição (description)
- Extrair critérios de aceitação
- Extrair anexos relevantes (imagens, documentos)
- Extrair links de suporte referenciados no ticket
- Extrair comentários (podem conter informações relevantes)
- Verificar se houve alterações desde a última execução
- Determinar qual AC deve ser implementada a seguir, consultando o histórico de execuções

Regras:
- Identificar critérios de aceitação:
    - procurar por seções como "Acceptance Criteria", "AC" ou listas
    - converter critérios em uma lista de strings
- Caso não existam critérios de aceitação:
    - retornar uma lista vazia
- Remover formatação desnecessária (HTML/Markdown)
- Caso título ou descrição não existam:
  - retornar string vazia
- Priorizar critérios vindos de campos estruturados
- Caso não existam, buscar na descrição
- Anexos e links são importantes para validar a alteração necessária — incluí-los sempre que existirem

## Steps

1. get-ticket
   - call: mcp.atlassian.get_info
   - input:
     jira_ticket_id: jira_ticket_id

2. get-linked-issues
   - call: mcp.atlassian.get_linked_issues
   - input:
     issueIdOrKey: jira_ticket_id
   - on_error: return_empty_array
   - logic:
     - If linked issues found:
       - For each linked issue, fetch its details using get_info
       - Extract: title, description, acceptance_criteria
       - Store in linked_issues array
     - Include linked issues context in the output for better understanding

3. get-attachments
   - call: mcp.atlassian.get_attachments
   - input:
     issueIdOrKey: jira_ticket_id
   - on_error: return_empty_array

3. get-links
   - call: mcp.atlassian.get_issue_remote_links
   - input:
     issueIdOrKey: jira_ticket_id
   - on_error: return_empty_array

4. get-comments
   - call: mcp.atlassian.get_comments
   - input:
     issueIdOrKey: jira_ticket_id
   - on_error: return_empty_array

5. get-history
   - call: mcp.filesystem.read_file
   - input:
     path: ".workflow/history/{jira_ticket_id}.json"
   - on_error: create_empty

6. get-snapshot
   - call: mcp.filesystem.read_file
   - input:
     path: ".workflow/history/{jira_ticket_id}_snapshot.json"
   - on_error: return_empty_object

7. detect-changes
   - input: current ticket data from steps 1-4, snapshot from step 6
   - logic:
     - if snapshot is empty:
       - this is first run → save snapshot and return no changes
     - else:
       - compare: title, description, acceptance_criteria, attachments, links, comments
       - report any differences found
       - return list of changes

8. save-snapshot
   - call: mcp.filesystem.write_file
   - input:
     path: ".workflow/history/{jira_ticket_id}_snapshot.json"
     content: current ticket snapshot (title, description, acceptance_criteria, attachments, links, comments, timestamp)

9. compute-next-ac
    - input: acceptance_criteria from step 1, history from step 5
    - logic:
      - if history is empty or history.completed_acs is empty:
        - current_ac_index = 0
      - else if history.current_ac_index is defined:
        - current_ac_index = history.current_ac_index
      - else:
        - current_ac_index = length of history.completed_acs
      
      - if acceptance_criteria is empty or length == 0:
        - This is a bug ticket without ACs
        - total_ac_count = 1 (treat as single fix task)
        - if current_ac_index == 0:
          - all_done = false
          - current_ac = "Fix the bug described in the ticket description"
        - else:
          - all_done = true
          - current_ac = ""
      - else:
        - total_ac_count = history.total_ac_count if defined, else length of acceptance_criteria
        - if current_ac_index >= total_ac_count:
          - all_done = true
          - current_ac = ""
        - else:
          - all_done = false
          - current_ac = acceptance_criteria[current_ac_index]

10. check-existing-plan
    - call: mcp.filesystem.search_files
    - input:
      path: "~/Development/teamwill/mobilize/workflow/plans"
      pattern: "*{jira_ticket_id}*ac{current_ac_index}*"
    - on_error: return_empty_array
    - logic:
      - if files found:
        - read the first matching plan file content
        - existing_plan = { found: true, path: file_path, content: file_content }
      - else:
        - existing_plan = { found: false }

 11. get-rag-resources
     - logic:
       - RAG resources can be in two locations:
         1. Local: `.workflow/RAG/` (project folder)
         2. OneDrive: `/Users/marcio_oliveira/Library/CloudStorage/OneDrive-TEAMWILLCONSULTING/TW Digital/Mobilize/RAG`
       
       - Check local RAG first:
         - search `.workflow/RAG/sprint_*/` for sprint-specific folders
         - search `.workflow/RAG/{jira_ticket_id}/` for ticket-specific resources
       
       - Check OneDrive RAG if not found locally:
         - search the OneDrive RAG path for matching folders
       
       - Build rag_resources = list of { api_name, spec_path, filename, source: 'local' | 'onedrive' }

12. present-changes
    - input: changes_detected from step 7
    - logic:
      - if changes_detected.length > 0:
        - ask user: "Foram detectadas alterações no ticket desde a última execução:"
          - list each change
          - "Deseja continuar com a implementação da AC ou cancelar?"
      - else: proceed normally

13. format-output
    - input: attachments from step 2, links from step 3, existing_plan from step 10, rag_resources from step 11
    - logic:
      - attachments = list of { filename, mimeType, url } for each attachment
      - links = list of { title, url } for each remote link
      - existing_plan = { found: true, path, content } or { found: false }
      - rag_resources = list of { api_name, spec_path, filename } for each OpenAPI spec, sprint support file, and workflow RAG file found

Formato de saída:
```json
{
  "title": "",
  "description": "",
  "acceptance_criteria": [],
  "current_ac": "",
  "current_ac_index": 0,
  "total_ac_count": 3,
  "all_done": false,
  "attachments": [],
  "links": [],
  "existing_plan": {
    "found": true,
    "path": "~/Development/teamwill/mobilize/workflow/plans/mmh-1435_ac0_plan.md",
    "content": "..."
  },
  "rag_resources": [
    { "api_name": "sprint_01", "spec_path": ".workflow/RAG/sprint_01", "filename": "sprint_requirements.md" },
    { "api_name": "mmh_1435", "spec_path": ".workflow/RAG/MMH_1435", "filename": "Asset Tab V1.xlsx" }
  ],
  "changes_detected": [
    { "field": "description", "before": "...", "after": "..." },
    { "field": "acceptance_criteria[1]", "before": "...", "after": "..." }
  ]
}
```