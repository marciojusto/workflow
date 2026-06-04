---
name: gitnexus-scan
description: "Optional deep code analysis using GitNexus. Use when miles-expert suggests it based on heuristic evaluation - typically for multi-module changes, unclear bugs, or refactoring with uncertain impact. Invoked after step 0.5 (analyze-with-miles-expert)."
---

# GitNexus Scan - Deep Code Analysis

## When to Use

Invoked **after** step 0.5 (analyze-with-miles-expert) when:
- miles-expert suggests it based on heuristic evaluation
- user accepts the suggestion
- Before create-plan (step 2) to get enhanced context

## Heuristics for Suggestion

**Use GitNexus when:**
- Impact multi-module detected (affects >1 cluster)
- Bug with non-obvious root cause
- Refactoring structural changes
- Low familiarity with code zone
- Suspected implicit dependencies
- Need blast radius before planning
- High regression risk

**Don't use when:**
- Small, localized change
- Clearly known area
- Simple, isolated, low-risk ticket
- Superficial validation sufficient
- Cost > expected value

## Input

```json
{
  "project_type": "hyperfront | deal-bs",
  "jira_ticket_id": "PROJ-123",
  "title": "Bug: Login fails for B2B customers",
  "description": "...",
  "acceptance_criteria": ["AC1", "AC2"],
  "domain_analysis": "...",
  "risk_areas": ["auth", "payments"],
  "affected_files": ["src/auth/login.ts"]
}
```

## Workflow

```
1. CHECK INDEX STATUS
   └─ gitnexus_detect_changes() → verify index is fresh
   └─ If stale: run npx gitnexus analyze in repo

2. IDENTIFY TARGET SYMBOLS
   ├─ Analyze domain_analysis to find key symbols
   ├─ If specific files mentioned → use as entry points
   └─ If abstract → query with gitnexus_query

3. RUN IMPACT ANALYSIS (gitnexus_impact)
   ├─ direction: "upstream" (what depends on this)
   ├─ direction: "downstream" (what does this depend on)
   └─ maxDepth: 3 for comprehensive analysis

4. GET EXECUTION FLOW CONTEXT
   └─ READ gitnexus://repo/{name}/processes
   └─ Identify which flows touch the affected symbols

5. ANALYZE SYMBOL RELATIONSHIPS
   ├─ gitnexus_context() for central symbols
   └─ Identify call chains and module boundaries

6. GENERATE IMPACT REPORT
```

## Tools

### gitnexus_impact
```typescript
gitnexus_impact({
  target: "validateUser",        // symbol or file
  direction: "upstream",         // upstream | downstream
  minConfidence: 0.8,
  maxDepth: 3
})
```

### gitnexus_query
```typescript
gitnexus_query({
  query: "authentication flow",  // semantic query
  limit: 10
})
```

### gitnexus_context
```typescript
gitnexus_context({
  name: "validateUser",
  includeCallees: true,
  includeCallers: true
})
```

### gitnexus_detect_changes
```typescript
gitnexus_detect_changes({scope: "staged"})
```

## Output

```json
{
  "impact_analysis": {
    "primary_affected_files": ["src/auth/login.ts", "src/api/middleware.ts"],
    "secondary_affected_files": ["src/routes/auth.ts"],
    "upstream_dependencies": ["loginHandler", "apiMiddleware"],
    "downstream_dependencies": ["sessionManager"],
    "blast_radius": "HIGH|MEDIUM|LOW"
  },
  "symbol_analysis": {
    "central_symbols": ["validateUser"],
    "call_chains": ["loginHandler → validateUser → checkPassword"],
    "module_boundaries": ["auth", "api", "routes"]
  },
  "execution_flows_affected": ["LoginFlow", "TokenRefresh"],
  "recommendations": {
    "files_to_review": ["src/auth/login.ts:42"],
    "tests_to_verify": ["tests/auth/login.spec.ts"],
    "potential_issues": ["session timeout edge case"]
  },
  "confidence": 0.85
}
```

## Integration with miles-expert

```
┌─────────────────────────────────────────────────┐
│             ANALYZE-WITH-MILES-EXPERT           │
│                   (step 0.5)                    │
└─────────────────────────────────────────────────┘
                      │
                      ▼
              miles-expert evaluates
              "Should I suggest gitnexus?"
                      │
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
      NÃO USAR             USAR + PERGUNTAR
      (simples)           "Deseja executar
                          gitnexus-scan?"
                              │
                              ▼
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
             create-plan          GITNEXUS-SCAN
             (basic only)         → enhanced context
                                       │
                                       ▼
                                Refinar análise
                                + create-plan
```

## Risk Assessment

| Affected              | Risk     | Action                        |
| --------------------- | -------- | ------------------------------ |
| <5 symbols, 1 flow    | LOW      | Proceed with basic plan       |
| 5-15 symbols, 2-5 flows| MEDIUM  | Enhanced review required      |
| >15 symbols, >5 flows | HIGH     | Detailed impact report needed |
| Critical path         | CRITICAL | Full regression testing       |

## Checklist

```
- [ ] Verify index freshness (gitnexus_detect_changes)
- [ ] Identify target symbols from domain_analysis
- [ ] Run gitnexus_impact (upstream + downstream)
- [ ] Check affected execution flows
- [ ] Generate impact report
- [ ] Pass enhanced context to miles-expert
- [ ] Proceed to create-plan with full context
```

## Example

**Input:** Ticket PROJ-123, "Fix login for B2B", domain_analysis says auth module affected

**Action:**
1. `gitnexus_impact({target: "loginHandler", direction: "upstream"})`
2. `READ gitnexus://repo/hyperfront/processes`
3. Identify: LoginFlow, TokenRefresh, AuthMiddleware affected

**Output:**
- blast_radius: MEDIUM
- files_to_review: 3
- Add to plan: "Verify auth flows: LoginFlow, TokenRefresh"

---

> **Note:** This skill is OPTIONAL. Use only when miles-expert suggests it and user accepts.