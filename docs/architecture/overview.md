# Architecture Overview

High-level architecture of the workflow system.

## Core Components

### 1. Orchestrator (`workflow-orchestrator`)

The primary coordinator that manages the complete workflow lifecycle.

**Responsibilities:**
- Session management (create, pause, resume, complete)
- Step logging and tracking
- Error handling and escalation
- Mode-specific flows (auto/plan/build)
- Agent delegation

**Key Features:**
- Preflight validation
- Parallel E2E execution
- Snapshot integration
- Rollback support

### 2. Workflow Implementation (`workflow-implementation`)

The main execution skill that handles the actual implementation.

**Steps:**
1. Mode selection (nova/bug/validar/continuar)
2. Project type detection
3. Task tracker detection
4. Context gathering (ticket or standalone)
5. Expert analysis (optional)
6. Spec-driven planning (tlc-spec-driven)
7. Teach mode (optional)
8. Plan creation and validation
9. Execution and testing
10. History logging

### 3. Supporting Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| `wiki-keeper` | Knowledge management | qwen3.5-flash |
| `business-expert` | Domain analysis | minimax-m2.7 |
| `validator` | Test execution | step-3.7-flash |
| `coherence-checker` | Architecture validation | - |
| `review-plan` | Plan review | GLM 5.1 |
| `e2e-runner` | E2E test runner | Step 3.5 Flash |

### 4. Skills

| Skill | Purpose |
|-------|---------|
| `tlc-spec-driven` | 4-phase planning (Specify, Design, Tasks, Execute) |
| `workflow-implementation` | Main implementation workflow |
| `workflow-logger` | Logging and session management |
| `grill-with-docs` | Interview/ADR generation |
| `teach` | Plan explanation |
| `extract-ticket` | Ticket extraction from trackers |

## Data Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  Orchestrator   │──► Creates session, loads config
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Extract/Grill  │──► Gets ticket or standalone context
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Business Expert │──► Optional domain analysis
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ tlc-spec-driven │──► SPECIFY + DESIGN phases
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Create Plan    │──► Implementation plan with principles
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Validate Plan  │──► plan-validator.py (quality ≥ 70)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Human Approval  │──► User must approve before execution
└─────────────────┘
    │
    ▼
┌─────────────────┐
│    Snapshot     │──► snapshot-manager.py creates backup
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Execute Plan  │──► Actual code changes
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Coherence Check│──► Architecture validation
└─────────────────┘
    │
    ▼
┌─────────────────┐
│    Run Tests    │──► Unit, integration, E2E
└─────────────────┘
    │
    ▼
┌─────────────────┐
│   Log History   │──► Record completion
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Complete Session│──► Archive session, update wiki
└─────────────────┘
```

## State Management

### Installer State (`~/.workflow-installer-state.json`)

```json
{
  "version": "2.0.0",
  "workflow_root": "~/workflow",
  "tools": {...},
  "providers": {...},
  "business_expert": {...},
  "tracker": {...},
  "sessions": {
    "abc123": {
      "session_id": "abc123",
      "workflow_id": "MMH-1435",
      "status": "running",
      "current_step": "execute-plan",
      "current_ac_index": 2,
      "checkpoints": [...]
    }
  },
  "current_session_id": "abc123",
  "workflow_history": [...]
}
```

### Session Lifecycle

1. **Create** — At workflow start
2. **Update** — After each step
3. **Pause** — On user request or error
4. **Resume** — When user continues
5. **Complete** — At workflow end

## Snapshot System

**Purpose:** Enable rollback to known-good states.

**When snapshots are created:**
- Before `execute-plan` (plans, specs, source)
- Before `run-tests` (tests, reports)
- After `log-history` (history files)

**Storage:** `~/.workflow/snapshots/<session_id>/`

**Retention:** Last 10 snapshots per session

## Logging System

**Format:** NDJSON (newline-delimited JSON)

**Location:** `logs/step-log.ndjson`

**Fields:**
- `timestamp` — ISO 8601
- `workflow_id` — Ticket or workflow ID
- `session_id` — Session identifier
- `agent` — Agent name
- `step` — Step name
- `event` — start/end/log
- `status` — in_progress/success/failure/skipped
- `description` — Step description
- `duration_ms` — Execution time
- `output_summary` — Result summary
- `error` — Error message (if any)

## Error Handling

### Types

| Type | Action | Limit |
|------|--------|-------|
| Timeout | Retry 2x, then fallback model | 3 attempts |
| Model/Provider Error | Fallback immediately | 1 fallback |
| Output Invalid | Retry with feedback | 1 retry |
| Rejected | Loop back with feedback | 2 iterations |

### Escalation

After 3 consecutive failures:
1. Pause session
2. Notify user with options:
   - Skip and continue
   - Manual fix and resume
   - Abort workflow

## Security Considerations

- API keys stored in environment variables
- Tracker MCP is READ-ONLY by default
- Write operations require explicit authorization
- Snapshots contain only workflow data (no secrets)

## Performance

- Parallel E2E execution for 3+ ACs (50-67% faster)
- Cached knowledge queries
- Incremental snapshot creation
- Efficient log rotation
