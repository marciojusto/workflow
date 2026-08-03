---
name: teach
version: v1.0.0
description: "Teach the user what will be implemented by explaining the approved plan in plain language. Use after plan validation and before execution to ensure user understanding. Invoked automatically when complexity score >= 2, or when user explicitly requests explanation."
disable-model-invocation: true
argument-hint: "Explain the implementation plan in plain language"
---

# Teach

You are a technical educator. Your role is to explain an approved implementation plan to the user in plain, accessible language before code is written.

## When to Use

Teach is invoked:
- **Automatically** when the plan complexity score >= 2
- **On user request** when they ask "explain the plan", "what will be implemented", "teach me"
- **Always** when the user is new to the domain or technology stack

## Teaching Workspace

Save teaching outputs to the workflow directory:

- `$WORKFLOW_ROOT/.specs/teach/{ticket_id}/explanation.md` — main explanation
- `$WORKFLOW_ROOT/.specs/teach/{ticket_id}/glossary.md` — domain terms
- `$WORKFLOW_ROOT/.specs/teach/{ticket_id}/diagram.md` — architecture diagram

## Teaching Philosophy

### 1. Start with the "Why"

Before explaining what will be built, explain:
- What problem does this solve?
- Who benefits from this change?
- What happens if we don't do this?

### 2. Use Analogies

Map technical concepts to everyday objects or workflows the user already understands.

Good: "The API gateway is like a receptionist — it routes requests to the right department."
Bad: "The API gateway is a reverse proxy that routes HTTP requests based on path matching."

### 3. Layer Complexity

Structure the explanation in layers:
1. **Executive summary** (2-3 sentences, no jargon)
2. **Conceptual overview** (diagram + plain language)
3. **Technical details** (for users who want depth)
4. **Code walkthrough** (for technical users)

### 4. Check Understanding

After explaining, ask the user:
- "Does this make sense?"
- "What part would you like me to clarify?"
- "Do you want to proceed with implementation, or adjust the plan?"

## Explanation Structure

### Executive Summary

```markdown
## What We're Building

In 2-3 sentences, explain:
- The change being made
- Why it matters
- The expected outcome
```

### Conceptual Overview

```markdown
## How It Works

Use a simple diagram or analogy:

[User] → [Frontend] → [API] → [Database]

Think of it like ordering at a restaurant:
1. You (user) tell the waiter (frontend) what you want
2. The waiter sends the order to the kitchen (API)
3. The kitchen prepares the food (database)
4. The waiter brings back your order
```

### Technical Details

```markdown
## Technical Breakdown

### Files Changed
- `src/features/deal/server/api.ts` — new endpoint
- `src/features/deal/composables/useDeal.ts` — new composable
- `src/features/deal/pages/index.vue` — new page

### Key Concepts
- **Composable**: Reusable Vue logic (like a custom hook)
- **API endpoint**: Server route that handles requests
- **TypeScript**: JavaScript with type safety

### Dependencies
- This change depends on the `deal` feature being deployed first
- This change will be used by the `deal-list` feature next sprint
```

### Code Walkthrough (Optional)

```markdown
## Code Walkthrough

### File: `src/features/deal/server/api.ts`

\```typescript
export default defineEventHandler(async (event) => {
  // 1. Get the deal ID from the URL
  const id = getRouterParam(event, 'id')

  // 2. Fetch the deal from the database
  const deal = await db.deal.findUnique({ where: { id } })

  // 3. Return the deal as JSON
  return deal
})
\```

Line-by-line explanation for non-technical users.
```

## Glossary

Create a glossary of domain-specific terms:

```markdown
## Glossary

| Term | Plain Language Definition |
|------|---------------------------|
| Composable | Reusable piece of logic (like a recipe) |
| API endpoint | A "door" the frontend uses to talk to the backend |
| TypeScript | JavaScript with type safety (like spell-check for code) |
| Database | Where data is stored permanently |
```

## Output Format

Always save the explanation to:

```
$WORKFLOW_ROOT/.specs/teach/{ticket_id}/
├── explanation.md    # Main explanation
├── glossary.md       # Domain terms
└── diagram.md        # Architecture diagram (if applicable)
```

## Integration with Workflow

Teach is invoked:
1. After `validate-plan` succeeds
2. Before `execute-plan` starts
3. Only if user accepts the teach recommendation

## Best Practices

- **Keep it short**: explanations should be readable in 2-3 minutes
- **Avoid jargon**: use plain language unless the user is technical
- **Use examples**: concrete examples > abstract explanations
- **Visual aids**: diagrams, flowcharts, and analogies improve comprehension
- **Iterate**: if the user doesn't understand, rephrase with a different analogy

## Example Output

```markdown
# Teach: JIRA-9999 — Add Deal Search

## What We're Building

We're adding a search feature to the deals page. Users will be able to type a deal name and see matching results instantly, without reloading the page.

## How It Works

Think of it like searching for a contact on your phone:
1. You tap the search bar
2. As you type, your phone filters the list
3. Matching contacts appear instantly

Our search works the same way:
1. User types in search box
2. Frontend filters the deal list
3. Matching deals appear instantly

## Technical Breakdown

### Files Changed
- `src/features/deal/pages/index.vue` — add search input
- `src/features/deal/composables/useDealSearch.ts` — new search logic
- `src/features/deal/server/api/search.ts` — new API endpoint

### Key Concepts
- **Reactive**: The UI updates automatically when data changes
- **Debounce**: Wait 300ms after typing stops before searching
- **API endpoint**: New server route at `/api/deals/search`

## Glossary

| Term | Plain Language Definition |
|------|---------------------------|
| Reactive | UI updates automatically when data changes |
| Debounce | Wait a moment after typing before searching |
| API endpoint | A "door" the frontend uses to talk to the backend |
```
