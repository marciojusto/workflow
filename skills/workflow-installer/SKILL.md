---
name: workflow-installer
version: v2.0.0
description: Install and bootstrap the workflow with all dependencies, skills, agents, and configuration. Tool-agnostic installer supporting OpenCode, Claude Code, Cursor, Codex, Windsurf, and custom AI coding tools. Run once on a fresh machine to set up the entire development environment.
---

# Workflow Installer

Install the complete workflow stack with one command. Handles dependencies, skills, agents, configuration, and verification for any AI coding tool.

## What This Installs

| Component | Destination | Purpose |
|-----------|-------------|---------|
| `tlc-spec-driven` | Selected tools' skills dir | Spec-driven development skill (4-phase planning) |
| `workflow-implementation` | Selected tools' skills dir | Main implementation workflow skill |
| `workflow-orchestrator` | Selected tools' agents dir | Primary orchestrator agent |
| `business-expert-*` | Workflow agents dir | Custom domain analysis agent (optional) |
| `coherence-checker` | Selected tools' agents dir | Architecture validation agent |
| `review-plan` | Selected tools' agents dir | Plan review agent |
| `e2e-runner` | Selected tools' agents dir | E2E test runner agent |
| `wiki-keeper` | Selected tools' agents dir | Knowledge management agent |
| `vision-describer` | Selected tools' agents dir | Vision/image analysis agent |
| `grill-with-docs` | Selected tools' skills dir | Interview/ADR skill (optional) |
| `GitNexus` | npm global | Code intelligence/knowledge graph |
| `playwright` | npm global | Browser automation/E2E testing |
| `sonar-scanner` | `~/.local/bin/` | SonarQube code analysis (native ARM64) |

## Prerequisites Check

Before installing, verify these are present:

| Tool | Required | Check Command | Install if Missing |
|------|----------|---------------|-------------------|
| Node.js | >= 18 | `node --version` | https://nodejs.org |
| npm | >= 9 | `npm --version` | Comes with Node.js |
| Git | >= 2.30 | `git --version` | https://git-scm.com |
| Python | >= 3.10 | `python3 --version` | https://python.org |
| Docker | >= 24 | `docker --version` | https://docker.com |

## Installation

### Quick Start

```bash
# Clone the workflow repository
git clone https://github.com/marciojusto/workflow.git ~/workflow
cd ~/workflow

# Run the interactive installer
bash scripts/install-workflow.sh
```

### Windows (PowerShell)

```powershell
# Clone the repository
git clone https://github.com/marciojusto/workflow.git $HOME\workflow
cd $HOME\workflow

# Run the PowerShell wrapper
.\scripts\Install-Workflow.ps1
```

## Installation Steps

The installer guides you through 8 sequential steps:

### Step 1: Workflow Directory

Choose where to install the workflow:
- `~/workflow` (recommended — global, shared across projects)
- `./workflow` (in current project directory)
- Custom path

If an existing installation is detected, you can:
- Use existing (skip)
- Overwrite (with automatic backup)
- Cancel

### Step 2: Global Packages

Installs required global npm packages:
- GitNexus (code intelligence)
- Playwright MCP (browser automation)
- SonarQube scanner (code analysis)

### Step 3: Business Expert (Optional)

Configure a custom domain expert agent:
- Name (e.g., `finance-expert`, `healthcare-expert`)
- Description
- Knowledge paths (docs, wikis, specs)
- Primary model
- Fallback model

If skipped, the workflow functions without a domain expert.

### Step 4: AI Coding Tools

Select which AI coding tools to configure:
- OpenCode
- Claude Code
- Cursor
- Codex
- Windsurf
- Custom (provide name + config directory)

For each tool:
- Config directory (auto-detected or custom)
- Install mode: `symlink` (single source of truth) or `copy` (isolated)
- Config file: provide existing file or let installer generate

### Step 5: LLM Providers

Select which LLM providers to configure:
- Kilo Gateway
- OpenAI
- Anthropic
- Google
- OpenRouter
- Ollama (local)
- Custom (provide baseURL + format)

For each provider:
- API key (optional, can be configured later)
- Default model (chosen from provider's model list)

### Step 6: Tool Configuration

The installer generates/updates config files for each selected tool based on the chosen providers.

### Step 7: Workflow Directories

Creates the workflow directory structure:
- `.specs/{project,codebase,features,quick,grill}/`
- `plans/`
- `scripts/`
- `logs/`

### Step 8: Verification

Checks that all components are correctly installed and configured.

## Post-Installation

### 1. Configure API Keys

Add API keys to your shell rc file (`.bashrc`, `.zshrc`, etc.):

```bash
export KILO_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-api-key-here"
# etc.
```

### 2. Restart Your AI Tool

Close and reopen your AI coding tool to load all new skills and agents.

### 3. Verify Installation

```bash
# For OpenCode
opencode skill list
opencode agent list

# Check state file
cat ~/.workflow-installer-state.json
```

### 4. First Run

```bash
# Test the workflow
opencode run "Hello, workflow!" --model=kilogateway/kimi-k2.5
```

## State File

The installer creates `~/.workflow-installer-state.json` to track:

```json
{
  "version": "2.0.0",
  "workflow_root": "~/workflow",
  "tools": {
    "opencode": {
      "config_dir": "~/.config/opencode",
      "install_mode": "symlink",
      "config_file": "opencode.json"
    }
  },
  "providers": {
    "kilogateway": {
      "default_model": "kimi-k2.5"
    }
  },
  "business_expert": {
    "name": "finance-expert",
    "description": "...",
    "model": "kilogateway/kimi-k2.5"
  },
  "installed_at": "2026-01-15T10:00:00Z"
}
```

## Re-Execution

You can re-run the installer at any time:
- Detects existing installation via state file
- Allows adding/removing tools, providers, or business expert
- Creates backups before modifying existing configs

## Migration

If you have an existing TeamWill installation, the installer will automatically detect it and offer to migrate:

```
Detectada instalação antiga do OpenCode
Deseja migrar para o novo formato? (s/n)
```

Migration preserves:
- Existing workflow files
- Business expert configuration (miles-expert)
- Provider settings
- Tool configurations

## Uninstallation

To remove the workflow completely:

```bash
# Remove workflow directory
rm -rf ~/workflow

# Remove state file
rm ~/.workflow-installer-state.json

# Remove global npm packages
npm uninstall -g gitnexus
npm uninstall -g @playwright/mcp

# Remove sonar-scanner
rm -rf ~/.local/bin/sonar-scanner

# Remove tool-specific configs (optional)
rm -rf ~/.config/opencode/skills/tlc-spec-driven
rm -rf ~/.config/opencode/skills/workflow-implementation
rm -rf ~/.config/opencode/agents/*
```

## Troubleshooting

### Installer doesn't detect existing installation
- Check that `~/.workflow-installer-state.json` exists
- Manually create state file if needed

### Tool doesn't see new skills/agents
- Restart the tool completely
- Check the tool's skills/agents directory
- Verify symlinks (if using symlink mode)

### Config file not generated
- Check installer logs for errors
- Verify the tool's config directory exists
- Try providing an existing config file manually

### State file corrupted
- Delete `~/.workflow-installer-state.json`
- Re-run installer

## Support

- Workflow repo: https://github.com/marciojusto/workflow
- OpenCode docs: https://opencode.ai/docs
- Kilo Gateway: https://kilo.ai/gateway
