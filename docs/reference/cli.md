# CLI Reference

Complete reference for the `workflow.py` command-line interface.

## Synopsis

```bash
python3 $WORKFLOW_ROOT/scripts/workflow.py <command> [args]
```

## Session Commands

### `session-create`

Create a new workflow session.

```bash
python3 workflow.py session-create <workflow_id> [mode]
```

**Arguments:**
- `workflow_id` — Ticket or workflow identifier (e.g., MMH-1435)
- `mode` — Execution mode: `auto`, `plan`, or `build` (default: auto)

**Example:**
```bash
python3 workflow.py session-create MMH-1435 auto
# Output: {"session_id": "abc123"}
```

### `session-get`

Get session details.

```bash
python3 workflow.py session-get [session_id]
```

**Arguments:**
- `session_id` — Optional. If omitted, returns current session.

**Example:**
```bash
python3 workflow.py session-get abc123
```

### `session-list`

List sessions with optional status filter.

```bash
python3 workflow.py session-list [status]
```

**Arguments:**
- `status` — Optional. One of: `running`, `paused`, `completed`, `failed`

**Example:**
```bash
python3 workflow.py session-list running
```

### `session-pause`

Pause a session with checkpoint.

```bash
python3 workflow.py session-pause [session_id] [reason]
```

**Arguments:**
- `session_id` — Optional. If omitted, pauses current session.
- `reason` — Optional. Reason for pause (default: user_request)

**Example:**
```bash
python3 workflow.py session-pause abc123 "waiting_for_review"
```

### `session-resume`

Resume a paused session.

```bash
python3 workflow.py session-resume <session_id>
```

**Example:**
```bash
python3 workflow.py session-resume abc123
```

### `session-complete`

Mark session as completed.

```bash
python3 workflow.py session-complete [session_id] [status]
```

**Arguments:**
- `session_id` — Optional. If omitted, completes current session.
- `status` — Optional. One of: `completed`, `failed`, `cancelled` (default: completed)

**Example:**
```bash
python3 workflow.py session-complete abc123 completed
```

## Log Commands

### `log-start`

Log step start.

```bash
python3 workflow.py log-start <wf_id> <agent> <step> [desc] [--session-id SID]
```

**Example:**
```bash
python3 workflow.py log-start MMH-1435 orchestrator init "Starting" --session-id abc123
```

### `log-end`

Log step end.

```bash
python3 workflow.py log-end <wf_id> <agent> <step> <status> [desc] [--session-id SID]
```

**Example:**
```bash
python3 workflow.py log-end MMH-1435 orchestrator init success "Done" --session-id abc123
```

### `log-view`

View logs with filters.

```bash
python3 workflow.py log-view [wf_id] [--tail N] [--status S] [--agent A]
```

**Examples:**
```bash
python3 workflow.py log-view MMH-1435
python3 workflow.py log-view --tail 20
python3 workflow.py log-view --status failure
python3 workflow.py log-view --agent miles-expert
```

### `log-status`

Show workflow status.

```bash
python3 workflow.py log-status <wf_id>
```

### `log-stats`

Show statistics.

```bash
python3 workflow.py log-stats [--days N]
```

## Validation Commands

### `validate-plan`

Validate implementation plan.

```bash
python3 workflow.py validate-plan <plan_path> [--current-ac TEXT] [--acs AC1 AC2...]
```

**Arguments:**
- `plan_path` — Path to plan markdown file
- `--current-ac` — Current acceptance criteria text
- `--acs` — List of all acceptance criteria

**Output:**
```json
{
  "is_valid": true,
  "quality_score": 85,
  "issues": [],
  "principles": {...},
  "clean_code": {...},
  "testing": {...},
  "coverage_score": 100,
  "threshold": 70
}
```

**Exit Code:**
- `0` — Plan is valid (score ≥ 70)
- `1` — Plan is invalid

**Example:**
```bash
python3 workflow.py validate-plan plans/MMH-1435_ac0_plan.md \
  --current-ac "User can login" \
  --acs "AC1" "AC2"
```

## Snapshot Commands

### `snapshot-create`

Create a manual snapshot.

```bash
python3 workflow.py snapshot-create <session_id> <snapshot_id> <paths...>
```

**Example:**
```bash
python3 workflow.py snapshot-create abc123 snap1 plans/ .specs/ src/
```

### `snapshot-list`

List snapshots for a session.

```bash
python3 workflow.py snapshot-list <session_id>
```

### `snapshot-latest`

Get latest snapshot for a session.

```bash
python3 workflow.py snapshot-latest <session_id>
```

### `rollback`

Rollback to a snapshot.

```bash
python3 workflow.py rollback <session_id> [--snapshot-id ID] [--target-dir DIR]
```

**Arguments:**
- `--snapshot-id` — Specific snapshot to restore (default: latest)
- `--target-dir` — Directory to restore to (default: temp dir)

**Examples:**
```bash
python3 workflow.py rollback abc123
python3 workflow.py rollback abc123 --snapshot-id snap1
python3 workflow.py rollback abc123 --target-dir /path/to/restore/
```

## Status Commands

### `status`

Show complete workflow status.

```bash
python3 workflow.py status
```

**Output includes:**
- Current active session
- Recent sessions
- Overall statistics

### `checkpoint`

Create manual checkpoint.

```bash
python3 workflow.py checkpoint <session_id> <step> <ac_index>
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKFLOW_ROOT` | Workflow installation directory | `~/workflow` |
| `STATE_FILE` | Installer state file path | `~/.workflow-installer-state.json` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Session not found |
| 4 | Validation failed |
| 5 | Snapshot not found |

## Examples

### Complete Workflow

```bash
# 1. Create session
SID=$(python3 workflow.py session-create MMH-1435 auto | jq -r .session_id)

# 2. Log start
python3 workflow.py log-start MMH-1435 orchestrator init "Starting" --session-id $SID

# 3. Validate plan
python3 workflow.py validate-plan plans/MMH-1435_plan.md --current-ac "User story"

# 4. Create snapshot
python3 workflow.py snapshot-create $SID pre-execute plans/ src/

# 5. Execute (via AI tool)
# ... implementation happens ...

# 6. Log completion
python3 workflow.py log-end MMH-1435 orchestrator complete success "Done" --session-id $SID

# 7. Complete session
python3 workflow.py session-complete $SID completed
```

### Recovery from Error

```bash
# List paused sessions
python3 workflow.py session-list paused

# Resume session
python3 workflow.py session-resume abc123

# Or rollback to last good state
python3 workflow.py rollback abc123

# Then resume
python3 workflow.py session-resume abc123
```
