---
name: log-history
version: v1.0.0
description: Registrar execução
---

# Log History

## Inputs
- jira_ticket_id
- current_ac_index
- current_ac
- total_acs
- implementation_summary
- files_changed
- code_changes

## Output
- log

## Instructions
Regista a conclusão de uma AC num ficheiro de histórico em formato Markdown.
Inclui informações detalhadas de todas as mudanças realizadas: ficheiros alterados, código adicionado/removido, e validações executadas.

Mantém também o ficheiro JSON `.workflow/history/{jira_ticket_id}.json` para navegação programática.

## Steps

1. read-json-history
   - call: mcp.filesystem.read_file
   - input:
      path: ".workflow/history/{jira_ticket_id}.json"
   - on_error: create_empty

2. append-to-json-history
   - input: history from step 1, current_ac_index, current_ac, total_acs, implementation_summary, files_changed
   - logic:
      - if history is empty or null:
        - history = { jira_ticket_id: jira_ticket_id, total_acs: total_acs, completed_acs: [], completion_percentage: 0 }
      - timestamp = current ISO 8601 timestamp
      - append to completed_acs: { index, ac, timestamp, summary, files_changed }
      - completion_percentage = round((completed_acs.length / total_acs) * 100)
      - history.total_acs = total_acs
      - return updated history object

3. write-json-history
   - call: mcp.filesystem.write_file
   - input:
      path: ".workflow/history/{jira_ticket_id}.json"
      content: history object from step 2 as JSON string

4. generate-markdown-log
   - input: all inputs (jira_ticket_id, current_ac_index, current_ac, total_acs, implementation_summary, files_changed, code_changes)
   - logic:
     - build markdown document with:
       - Header with ticket ID and AC number
       - Completion percentage badge (e.g., "40% (2/5 ACs)")
       - AC text
       - Implementation summary
       - Files changed (list with paths)
       - Code changes (diff-style or before/after blocks)
       - Timestamp
       - Attachments/links if any

5. write-markdown-history
   - call: mcp.filesystem.write_file
   - input:
      path: ".workflow/history/{jira_ticket_id}_ac_{current_ac_index}.md"
      content: markdown from step 4

6. append-to-main-log
   - call: mcp.filesystem.read_file
   - input:
      path: ".workflow/history/{jira_ticket_id}_log.md"
   - on_error: create_empty

7. append-entry
   - input: markdown from step 4, main_log from step 6
   - logic: append the new AC entry to the main log file

8. write-main-log
   - call: mcp.filesystem.write_file
   - input:
      path: ".workflow/history/{jira_ticket_id}_log.md"
      content: updated main log

Formato de saída:
```json
{
  "log": "AC {current_ac_index} registada com sucesso. Ficheiros alterados: {files_changed}"
}
```

Formato do ficheiro JSON `.workflow/history/{jira_ticket_id}.json`:
```json
{
  "jira_ticket_id": "PROJ-123",
  "total_acs": 5,
  "completion_percentage": 40,
  "completed_acs": [
    {
      "index": 0,
      "ac": "texto da AC",
      "timestamp": "2026-04-15T09:49:39.000Z",
      "summary": "resumo da implementação",
      "files_changed": ["src/foo/bar.vue"]
    }
  ]
}
```

Formato do ficheiro Markdown `.workflow/history/{jira_ticket_id}_ac_0.md`:
```markdown
# AC #0 — PROJ-123

**Ticket:** PROJ-123
**AC Index:** 0
**Completion:** 40% (2/5 ACs)
**Timestamp:** 2026-04-15T09:49:39.000Z

---

## Acceptance Criteria

Texto completo da AC implementada.

---

## Implementation Summary

Resumo da implementação executada.

---

## Files Changed

- `src/features/deals/components/DealStatus.vue`
- `composables/useDealsSync.ts`

---

## Code Changes

### src/features/deals/components/DealStatus.vue

```diff
- const status = ref('')
+ const status = ref<'pending' | 'approved' | 'rejected'>('pending')
```

---

## Validation

- [x] Code usage verified
- [x] E2E test passed

---