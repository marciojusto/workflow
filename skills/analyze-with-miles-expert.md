---
name: analyze-with-miles-expert
description: Invoke miles-expert for deep domain analysis with ticket data.
---

# Analyze with Miles Expert

## Config
retry: 1
on_error: report_and_continue

## Inputs
- jira_ticket_id
- title
- description
- acceptance_criteria
- current_ac
- current_ac_index
- total_ac_count
- project_type

## Outputs
- domain_analysis
- risk_areas
- dependencies
- technical_notes

## Instructions

This step invokes the miles-expert agent to perform deep domain analysis after ticket data has been extracted.

### When to Use
- After extract-jira-ticket step (0.3)
- Before create-plan step (2)
- When deep technical analysis is needed for complex tickets
- For bugs where root cause is not obvious
- For refactoring or structural changes
- When understanding cross-module dependencies is critical

### When NOT to Use
- Simple tasks with clear scope
- Small, localized changes
- When quick validation is sufficient

### Process
1. Prepare input for miles-expert:
   - Include title, description, acceptance_criteria
   - Include current_ac being worked on
   - Include project_type context

2. Invoke miles-expert with structured prompt:
   ```
   Analyze the following ticket for implementation planning:

   Ticket: {jira_ticket_id}
   Title: {title}
   Description: {description}

   Acceptance Criteria:
   {acceptance_criteria}

   Current AC: {current_ac} (index {current_ac_index} of {total_ac_count})

   Project Type: {project_type}

   Provide:
   1. Domain analysis: Key technical considerations
   2. Risk areas: Potential issues or complexities
   3. Dependencies: What other modules/components may be affected
   4. Technical notes: Architecture, patterns, or API considerations
   ```

3. Capture output as structured analysis for create-plan step

### Output Format
Return a JSON-like structure:
```json
{
  "domain_analysis": "...",
  "risk_areas": ["...", "..."],
  "dependencies": ["...", "..."],
  "technical_notes": "..."
}
```

This analysis will be passed to create-plan to inform the implementation strategy.