# Getting Started

Complete guide to setting up and using the workflow.

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Node.js | >= 18 | `node --version` |
| npm | >= 9 | `npm --version` |
| Python | >= 3.10 | `python3 --version` |
| Git | >= 2.30 | `git --version` |
| Docker | >= 24 | `docker --version` |

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/marciojusto/workflow.git ~/workflow
cd ~/workflow

# Run the interactive installer
bash scripts/install-workflow.sh
```

### Windows (PowerShell)

```powershell
git clone https://github.com/marciojusto/workflow.git $HOME\workflow
cd $HOME\workflow
.\scripts\Install-Workflow.ps1
```

## Post-Installation

### 1. Configure API Keys

Add to your shell rc file (`.bashrc`, `.zshrc`, etc.):

```bash
export KILO_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-api-key-here"
# etc.
```

### 2. Restart Your AI Tool

Close and reopen your AI coding tool to load new skills and agents.

### 3. Verify Installation

```bash
# Check state file
cat ~/.workflow-installer-state.json

# Test workflow CLI
python3 ~/workflow/scripts/workflow.py status
```

## Your First Workflow

### 1. Create a Session

```bash
python3 ~/workflow/scripts/workflow.py session-create MY-FEATURE auto
```

### 2. Run the Workflow

Using your AI tool (OpenCode example):

```bash
opencode run "Implement user authentication" --model=kilogateway/kimi-k2.5
```

### 3. Monitor Progress

```bash
# Check status
python3 ~/workflow/scripts/workflow.py status

# View logs
python3 ~/workflow/scripts/workflow.py log-view MY-FEATURE

# List sessions
python3 ~/workflow/scripts/workflow.py session-list
```

## Common Commands

| Command | Description |
|---------|-------------|
| `workflow.py session-create <id> <mode>` | Create new workflow session |
| `workflow.py session-list [status]` | List sessions |
| `workflow.py session-pause [id]` | Pause workflow |
| `workflow.py session-resume <id>` | Resume workflow |
| `workflow.py status` | Show overall status |
| `workflow.py log-view <id>` | View workflow logs |
| `workflow.py validate-plan <path>` | Validate implementation plan |
| `workflow.py snapshot-list <id>` | List snapshots |
| `workflow.py rollback <id>` | Rollback to snapshot |

## Configuration

### Task Tracker Setup

Edit `~/.workflow-installer-state.json`:

```json
{
  "tracker": {
    "type": "jira|redmine|github|gitlab|mock",
    "url": "https://your-tracker.com",
    "apiKey": "your-api-key"
  }
}
```

### Business Expert Setup

```json
{
  "business_expert": {
    "name": "your-expert",
    "description": "Domain expertise description",
    "model": "kilogateway/kimi-k2.5"
  }
}
```

## Troubleshooting

### Workflow won't start

1. Check preflight: `python3 ~/workflow/scripts/harness-health-check.py --preflight`
2. Verify API keys are set
3. Check logs: `python3 ~/workflow/scripts/workflow.py log-view --tail 20`

### Session stuck

```bash
# List paused sessions
python3 ~/workflow/scripts/workflow.py session-list paused

# Resume or complete
python3 ~/workflow/scripts/workflow.py session-resume <id>
# OR
python3 ~/workflow/scripts/workflow.py session-complete <id> cancelled
```

### Tests failing

1. Rollback to last good state:
   ```bash
   python3 ~/workflow/scripts/workflow.py rollback <session_id>
   ```

2. Check what changed:
   ```bash
   python3 ~/workflow/scripts/workflow.py snapshot-list <session_id>
   ```

## Next Steps

- Read the [Architecture Overview](../architecture/overview.md)
- Check the [CLI Reference](../reference/cli.md)
- Explore [Advanced Features](advanced-features.md)
