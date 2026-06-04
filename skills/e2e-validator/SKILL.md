---
name: e2e-validator
version: v1.0.1
description: Test the acceptance criteria using Playwright MCP + screenshots. Uses the e2e-runner agent with StepFun Step 3.5 Flash model.
---

# Playwright AC Validator

## Config
on_error: report_and_continue

## Inputs
- current_ac
- scope: "current_only" | "all"
- app_url (optional, defaults to http://localhost:3000)

## Output
- passed
- screenshot_path
- error_message
- contextId

## When use
- Use whenever asked to "test this AC", "test E2E", "check UI", "validate implementation"

## Guidelines
- When login expires and is requested to log in again, let the user log in
- When a popup Data Privacy is shown, click on sending by email
- When postal code is required, fill it with 35309
- When it is necessary to go to a proposal phase, the button will be enabled after the button send secci is clicked
- If scope == "current_only": validate only the AC provided in current_ac
- If scope == "all": validate all acceptance criteria for the ticket
- Take screenshots at key validation points
- Provide clear pass/fail feedback per AC

## Steps

1. invoke-e2e-runner-agent
   - call: task
   - input:
     command: Validate the acceptance criteria using Playwright
     subagent_type: e2e-runner
     prompt: |
       Validate the following acceptance criteria:
       
       - current_ac: {current_ac}
       - scope: {scope}
       - app_url: {app_url}
       
       Take screenshots at key validation points and provide clear pass/fail feedback.
       
       Guidelines:
       - When login expires, let the user log in again
       - When a Data Privacy popup appears, click on "sending by email"
       - When postal code is required, use 35309
       - The proposal phase button will be enabled after clicking "send secci"
       
       Return the results in this format:
       ```json
       {
         "passed": true,
         "screenshot_path": ".workflow/tests/e2e/screenshots/ac_validate.png",
         "error_message": null,
         "contextId": null
       }
       ```

       If an AC fails:
       ```json
       {
         "passed": false,
         "screenshot_path": ".workflow/tests/e2e/screenshots/ac_fail.png",
         "error_message": "AC 'user can see deal status' failed: expected status 'approved' but found 'pending'",
         "contextId": "DEV-XXXXXXXXXXXX-XXXXX-XXXX"
       }
       ```

       IMPORTANT: Always include the contextId in the error output when a test fails. The contextId is required for debugging and issue tracking.

2. extract-result
   - input: result from step 1
   - output: passed, screenshot_path, error_message, contextId