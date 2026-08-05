---
name: workflow-logger
version: v1.0.0
description: Unified logging and session management for workflow execution. Provides structured JSON logging, session pause/resume, and progress tracking.
---

# Workflow Logger

Centralized logging and session management for all workflow operations.

## Features

- **Structured Logging**: JSON format with timestamps, durations, and context
- **Session Management**: Pause/resume workflows, checkpointing
- **Progress Tracking**: Real-time status of running workflows
- **Integration**: Works with step-log.py and install-state.py

## Session Management

### Create Session

```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py session-create <workflow_id> <mode>
# Returns: {"session_id": "abc123"}
```

### Pause/Resume

```bash
# Pause current session
python3 $WORKFLOW_ROOT/scripts/workflow.py session-pause [session_id] [reason]

# Resume paused session
python3 $WORKFLOW_ROOT/scripts/workflow.py session-resume <session_id>

# List sessions
python3 $WORKFLOW_ROOT/scripts/workflow.py session-list [running|paused|completed|failed]
```

### Complete Session

```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py session-complete [session_id] [completed|failed|cancelled]
```

## Logging

### Log Step Start

```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py log-start <workflow_id> <agent> <step> [description] [--session-id SID]
```

### Log Step End

```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py log-end <workflow_id> <agent> <step> <status> [summary] [--session-id SID]
```

### View Logs

```bash
# View all logs for a workflow
python3 $WORKFLOW_ROOT/scripts/workflow.py log-view <workflow_id>

# View last N logs
python3 $WORKFLOW_ROOT/scripts/workflow.py log-view --tail 20

# Filter by status
python3 $WORKFLOW_ROOT/scripts/workflow.py log-view --status failure

# Filter by agent
python3 $WORKFLOW_ROOT/scripts/workflow.py log-view --agent miles-expert
```

### Workflow Status

```bash
# Overall status
python3 $WORKFLOW_ROOT/scripts/workflow.py status

# Specific workflow status
python3 $WORKFLOW_ROOT/scripts/workflow.py log-status <workflow_id>

# Statistics
python3 $WORKFLOW_ROOT/scripts/workflow.py log-stats [--days 7]
```

## Integration with Orchestrator

The orchestrator automatically:
1. Creates a session at workflow start
2. Logs each step with `--session-id`
3. Updates session state on each step
4. Completes session on workflow end

## Log Format

```json
{
  "timestamp": "2026-08-05T15:21:14.704684+00:00",
  "workflow_id": "MMH-1435",
  "session_id": "0506c91b",
  "agent": "orchestrator",
  "step": "init",
  "event": "start|end|log",
  "status": "in_progress|success|failure|skipped",
  "description": "Step description",
  "duration_ms": 101,
  "output_summary": "Result summary",
  "error": null
}
```

## Session Schema

```json
{
  "session_id": "0506c91b",
  "workflow_id": "MMH-1435",
  "mode": "auto|plan|build",
  "status": "running|paused|completed|failed|cancelled",
  "current_step": "execute-plan",
  "current_ac_index": 2,
  "total_acs": 4,
  "created_at": "2026-08-05T15:20:59Z",
  "updated_at": "2026-08-05T15:21:14Z",
  "paused_at": null,
  "completed_at": null,
  "context": {},
  "checkpoints": [
    {
      "timestamp": "2026-08-05T15:21:06Z",
      "step": "init",
      "ac_index": 0,
      "reason": "user_request"
    }
  ],
  "error": null
}
```

## Checkpointing

Checkpoints are created automatically when:
- Session is paused
- Critical steps complete
- Errors occur

Manual checkpoint:
```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py checkpoint <session_id> <step> <ac_index>
```

## Plan Validation

Use the advanced plan validator for comprehensive plan analysis:

```bash
# Validate a plan
python3 $WORKFLOW_ROOT/scripts/workflow.py validate-plan \
  $WORKFLOW_ROOT/plans/{ticket_id}_ac{ac_index}_plan.md \
  --current-ac "The user can login" \
  --acs "AC1" "AC2" "AC3"

# Output format
{
  "is_valid": true,
  "quality_score": 85,
  "issues": [],
  "principles": {"dry": "ok", "kiss": "ok", ...},
  "clean_code": {"small_functions": "ok", ...},
  "testing": {"given_when_then": "ok", ...},
  "coverage_score": 100,
  "threshold": 70
}
```

**Quality Score**: 0-100, threshold = 70
- < 70 → invalid, loop back to create-plan
- Issues prefixed: [STRUCTURE], [COVERAGE], [PRINCIPLE], [CLEAN_CODE], [TESTING]

## Snapshots and Rollback

Automatic snapshots before critical steps:

```bash
# Create manual snapshot
python3 $WORKFLOW_ROOT/scripts/workflow.py snapshot-create \
  <session_id> <snapshot_id> <paths...>

# List snapshots
python3 $WORKFLOW_ROOT/scripts/workflow.py snapshot-list <session_id>

# Get latest snapshot
python3 $WORKFLOW_ROOT/scripts/workflow.py snapshot-latest <session_id>

# Rollback to latest
python3 $WORKFLOW_ROOT/scripts/workflow.py rollback <session_id>

# Rollback to specific snapshot
python3 $WORKFLOW_ROOT/scripts/workflow.py rollback <session_id> --snapshot-id <id>

# Rollback to directory
python3 $WORKFLOW_ROOT/scripts/workflow.py rollback <session_id> --target-dir /path/
```

**Auto-snapshots** are created before:
- `execute-plan` — plans, specs, source code
- `run-tests` — tests, reports
- `log-history` — history files

**Retention**: Last 10 snapshots per session.

## Best Practices

1. **Always use session-id**: Pass `--session-id` to all log commands
2. **Log early, log often**: Log at the start and end of each step
3. **Pause on errors**: If a step fails, pause the session before retrying
4. **Resume carefully**: When resuming, verify the current step matches expectations
5. **Complete sessions**: Always complete sessions to keep history clean
6. **Validate plans**: Always run plan-validator before execute-plan
7. **Snapshot before changes**: Create snapshots before critical modifications
8. **Rollback when stuck**: Use rollback to return to a known-good state

## Error Handling

- If a session is not found, commands return `null` or error message
- If logging fails, the workflow continues (non-blocking)
- Sessions are persisted to `~/.workflow-installer-state.json`
- Logs are persisted to `logs/step-log.ndjson`
- Snapshots are persisted to `~/.workflow/snapshots/`
- Validation failures return quality score + specific issues
