---
name: tana-jira-sync
version: v1.0.0
description: For every Jira ticket, check/create node in Tana under today's daily note in the Marcio Justo workspace, using the tag WorkTask.
triggers: ["Jira", "ticket", "MMH-"]
priority: high
---
# Use the SKILL login-step first and after sync Jira → Tana (Do it first)

1. Extract Jira ticket ID from branch/context (ex: MMH-123).

2. If it doesn't exist in the branch, get it from the prompt used.

3. USE THE MCP tools already connected (Atlassian, Playwright and Tana)

4. The tana node needs to be based on other nodes with the same tag (tag: WorkTask)

5. Assign the node related to the ticket to me as a person (tag: Person)

6. Insert the today date and the time started