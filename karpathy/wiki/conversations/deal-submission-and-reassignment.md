# Deal Submission and Reassignment Process Review - 29/Jan/2026

- **Participantes**: Marcio and Rania
- **Data**: 29/Jan/2026
- **Tags**: `#conversa`, `#offer`, `#contract`, `#delivery`, `#hyperfront`

---

## Resumo

Review of the deal submission and reassignment process in the MMP system. Marcio and Rania walked through the complete deal lifecycle — from document upload and submission through to contract activation — and discussed the current limitation that deal reassignment is only possible in the simulation phase, with a Sofico ticket opened to extend it to other phases (pending proposal, under study, waiting for delivery).

## Notas

- Deal submission requires all mandatory fields filled and all 4 applicant/contract documents uploaded before "Save and Submit" is enabled
- After submission, status progresses: pending proposal → under study (auto-updated by cron) → waiting for delivery → contract activation
- The deal reassignment feature currently works **only** in the simulation/pending simulation phase
- A Sofico ticket was opened to fix reassignment in other phases (pending proposal, under study, waiting for delivery)
- Reassignment rules identified:
  1. Only possible within the same dealership
  2. Only before contract activation
  3. Allowed in all phases (target state)
- An update/save issue was blocking submissions during the session but was eventually resolved
- Marcio shared his screen via Citrix to demonstrate the process end-to-end
- Rania noted that a "re-attribute" button is available with a seller combo box to change the dealer

## Decisões / Action Items

- [ ] Verify Sofico ticket status for reassignment in all deal phases
- [ ] Confirm the dealership validation rule (same dealership check) is already implemented
- [ ] Test reassignment in pending simulation phase before extending to other phases
