# Clarifying Broker Terminology and Addressing API Deployment Challenges - 2026-05-14

- **Participants**: Marcio & Hendrik
- **Date**: 2026-05-14
- **Tags**: #conversa #party #deal-bs

---

## Summary

Conversation between Marcio and Hendrik covering two main topics: (1) clarification of broker/agent terminology in the MMP vs Miles ecosystem, where "broker" = dealership (company) and "broker contact" = salesperson (individual); (2) challenges in publishing new APIs via the API gateway, where Usama is the single point of contact for deployment, creating a development bottleneck.

## Notes

### Broker Terminology

- In Miles, the term "broker" refers to the dealership (broker company), not the individual salesperson.
- "Broker contact" is the salesperson — the natural person working at the dealership.
- MMP uses `brokerContactId` for the salesperson and `brokerCompanyId` for the dealership.
- The terminological confusion is compounded by inconsistent use of ubiquitous language across refinements and conversations — they use "seller", "sales person", "broker" interchangeably.
- Test setup created by Hendrik for dealership A:
  - **A M1** (Alberto Martin) — Manager of dealership A, can view and reassign deals.
  - **A S1** (Anna Serrano) — Salesperson at dealership A.
  - **A S2** (Andre Sanchez) — Salesperson at dealership A.
- A manager can reassign deals **only within the same dealership** (e.g., from A S1 to A S2).
- There are also cross-dealership users (T W X M1, T W X S1, T W X S2) assigned to both dealerships A and B, but this scenario has not yet been implemented in user stories.

### API Deployment Challenges

- The broker contacts API on the gateway is not functional — URL not available.
- Hendrik emailed Usama but received no response — there is a bottleneck because Usama is the only person who can deploy to the API gateway.
- The ideal process would be: DevOps should publish the APIs **before** the sprint starts, not during.
- Currently, when Usama and Bilal (ESP/API gateway team) are busy, the time when both are simultaneously available is rare.
- Hendrik suggests raising at the retro that "waiting for API deployment is delaying the project" and that everything should be open for the development environment.
- This is seen as a Mobilize problem (lack of dedicated people), not a development team problem.

### Other Technical Issues Mentioned

- **deal-bs (Reactor)**: Problems with async logging — log entries appear out of order because the project copied from another one did not use Log4j2 with Disruptor. Hendrik plans to fix it.
- **hyperfront (Nuxt/Pinia)**: Pinia was implemented in a way that states are not visible in Nuxt DevTools. Marcio already fixed this in another ticket but the feature branch has not been merged yet.
- **Logbook filter**: The Logbook filter (3 lines of code) was never added to the web client in deal-bs. Hendrik created a feature branch for Adil to merge, but Adil is busy with another user story.
- **Communication with DevOps**: The Tunisian team is used to being responsible for everything, and the business owners (Mobilize) have not learned to contact DevOps directly when the environment is down.

## Decisions / Action Items

- [ ] Hendrik will raise the API deployment bottlenecks at Friday's retro.
- [x] Clarified that "broker" in MMP = dealership and "broker contact" = salesperson.
- [x] Manager can reassign deals only within the same dealership.
- [x] Hendrik will fix async logging in deal-bs (Log4j2 with Disruptor).
- [ ] Feature branch with Logbook filter needs to be merged (blocked on Adil).
- [ ] Marcio's feature branch with Pinia DevTools fix needs to be merged.
