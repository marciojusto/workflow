---
name: workflow-installer
version: v1.0.0
description: Install and bootstrap the complete workflow with all dependencies, skills, agents, and configuration. Run once on a fresh machine to set up the entire development environment.
---

# Workflow Installer

Install the complete workflow stack with one command. Handles dependencies, skills, agents, configuration, and verification.

## What This Installs

| Component | Destination | Purpose |
|-----------|-------------|---------|
| `tlc-spec-driven` | `~/.config/opencode/skills/` | Spec-driven development skill (4-phase planning) |
| `workflow-implementation` | `~/.config/opencode/skills/` | Main implementation workflow skill |
| `workflow-orchestrator` | `~/.config/opencode/agents/` | Primary orchestrator agent |
| `miles-expert` | `~/.config/opencode/agents/` | Domain analysis agent (Kimi K2.5) |
| `coherence-checker` | `~/.config/opencode/agents/` | Architecture validation agent |
| `review-plan` | `~/.config/opencode/agents/` | Plan review agent (GLM 5.1) |
| `e2e-runner` | `~/.config/opencode/agents/` | E2E test runner agent |
| `vision-describer` | `~/.config/opencode/agents/` | Vision/image analysis agent |
| `wiki-keeper` | `~/.config/opencode/agents/` | Knowledge management agent |
| `validator` | `~/.config/opencode/agents/` | Test execution agent |
| `grill-with-docs` | `~/.config/opencode/skills/` | Interview/ADR skill (optional) |
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
| OpenCode | latest | `opencode --version` | https://opencode.ai |

## Installation Steps

### Step 1: Clone Workflow Repository

```bash
# Clone the workflow repository
git clone https://github.com/marciojusto/workflow.git ~/Development/teamwill/mobilize/workflow
cd ~/Development/teamwill/mobilize/workflow
```

### Step 2: Install Global npm Packages

```bash
# Install GitNexus (code intelligence)
npm install -g gitnexus

# Install Playwright (browser automation)
npm install -g @playwright/mcp@latest
npx playwright install --with-deps chromium
```

### Step 3: Install SonarQube Scanner

```bash
# Download native ARM64 sonar-scanner
mkdir -p ~/.local/bin
curl -L -o ~/.local/bin/sonar-scanner.zip \
  "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-8.1.0.6389-linux-arm64.zip"
unzip -q ~/.local/bin/sonar-scanner.zip -d ~/.local/bin/
mv ~/.local/bin/sonar-scanner-8.1.0.6389-linux-arm64 ~/.local/bin/sonar-scanner
chmod +x ~/.local/bin/sonar-scanner/sonar-scanner
rm ~/.local/bin/sonar-scanner.zip
```

### Step 4: Configure OpenCode

```bash
# Create OpenCode config directory
mkdir -p ~/.config/opencode

# Copy example config (if exists) or create minimal config
if [ -f workflow/MCPs/opencode.json ]; then
  cp workflow/MCPs/opencode.json ~/.config/opencode/opencode.json
else
  # Create minimal config with Kilo Gateway
  cat > ~/.config/opencode/opencode.json << 'EOF'
{
  "model": "kilogateway/kimi-k2.5",
  "provider": {
    "kilogateway": {
      "name": "Kilo Gateway",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "https://api.kilo.ai/api/gateway"
      },
      "models": {
        "kimi-k2.5": { "name": "Kimi K2.5", "id": "moonshotai/kimi-k2.5" },
        "kimi-k2.7-code": { "name": "Kimi K2.7 Code", "id": "moonshotai/kimi-k2.7-code" },
        "glm-5.2": { "name": "GLM 5.2", "id": "z-ai/glm-5.2" },
        "deepseek-v4-flash:free": { "name": "DeepSeek V4 Flash (free)", "id": "deepseek/deepseek-v4-flash:free" },
        "step-3.7-flash:free": { "name": "StepFun 3.7 Flash (free)", "id": "stepfun/step-3.7-flash:free" }
      }
    }
  },
  "mcp": {
    "Memory": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
      "enabled": true
    },
    "Filesystem": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/Users/marcio_oliveira/Development"],
      "enabled": true
    },
    "Playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp@latest"],
      "enabled": true
    },
    "GitNexus": {
      "type": "local",
      "command": ["npx", "-y", "gitnexus", "mcp"],
      "enabled": true
    }
  }
}
EOF
fi
```

**Note:** Update the Filesystem path in `opencode.json` to match your home directory if not `/Users/marcio_oliveira`.

### Step 5: Install OpenCode Skills

```bash
# Create skills directories
mkdir -p ~/.config/opencode/skills
mkdir -p ~/.config/opencode/agents

# Install tlc-spec-driven v3.1.0
cp -r workflow/skills/tlc-spec-driven ~/.config/opencode/skills/

# Install workflow-implementation
cp -r workflow/skills/workflow-implementation ~/.config/opencode/skills/

# Install agents
cp -r workflow/agents/* ~/.config/opencode/agents/

# Install grill-with-docs (optional)
mkdir -p ~/.config/opencode/skills/grill-with-docs
cat > ~/.config/opencode/skills/grill-with-docs/SKILL.md << 'EOF'
---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Run a `/grilling` session, using the `/domain-modeling` skill.
EOF
```

### Step 6: Create Workflow Directories

```bash
# Create .specs structure
mkdir -p workflow/.specs/{project,codebase,features,quick,grill}

# Create plans directory
mkdir -p workflow/plans

# Create scripts directory
mkdir -p workflow/scripts

# Create logs directory
mkdir -p workflow/logs
```

### Step 7: Install Project-Specific Skills

```bash
# Install in hyperfront
mkdir -p ~/Development/teamwill/mobilize/hyperfront/.claude/skills
cp -r workflow/skills/tlc-spec-driven ~/Development/teamwill/mobilize/hyperfront/.claude/skills/
cp -r workflow/skills/workflow-implementation ~/Development/teamwill/mobilize/hyperfront/.claude/skills/
cp workflow/agents/*.md ~/Development/teamwill/mobilize/hyperfront/

# Install in deal-bs
mkdir -p ~/Development/teamwill/mobilize/deal-bs/.claude/skills
cp -r workflow/skills/tlc-spec-driven ~/Development/teamwill/mobilize/deal-bs/.claude/skills/
cp -r workflow/skills/workflow-implementation ~/Development/teamwill/mobilize/deal-bs/.claude/skills/
cp workflow/agents/*.md ~/Development/teamwill/mobilize/deal-bs/
```

### Step 8: Configure SonarQube (Optional)

```bash
# Start SonarQube container
cd workflow/docker
docker compose up -d sonarqube

# Wait for SonarQube to be ready (about 2 minutes)
# Access at http://localhost:9000
# Default credentials: admin / admin
```

### Step 9: Verify Installation

```bash
# Verify OpenCode can see all skills
opencode skill list

# Verify agents are loaded
opencode agent list

# Verify GitNexus is working
gitnexus --version

# Verify Playwright is working
npx playwright --version

# Verify sonar-scanner is working
~/.local/bin/sonar-scanner/sonar-scanner --version
```

## Post-Installation

### 1. Set Kilo API Key

```bash
export KILO_API_KEY="your-api-key-here"
# Add to ~/.zshrc or ~/.bashrc for persistence
```

Get your API key at: https://kilo.ai/gateway

### 2. Configure Git (if not already done)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Restart OpenCode Desktop

Close and reopen OpenCode Desktop to load all new skills and agents.

### 4. First Run

```bash
# Test the workflow
opencode run "Hello, testing workflow installation" --model=kilogateway/kimi-k2.5
```

## Uninstallation

To remove the workflow completely:

```bash
# Remove OpenCode skills and agents
rm -rf ~/.config/opencode/skills/tlc-spec-driven
rm -rf ~/.config/opencode/skills/workflow-implementation
rm -rf ~/.config/opencode/skills/grill-with-docs
rm -rf ~/.config/opencode/agents/*

# Remove workflow repository
rm -rf ~/Development/teamwill/mobilize/workflow

# Remove sonar-scanner
rm -rf ~/.local/bin/sonar-scanner

# Remove npm packages
npm uninstall -g gitnexus
npm uninstall -g @playwright/mcp
```

## Troubleshooting

### OpenCode doesn't see new skills
- Restart OpenCode Desktop completely
- Check `~/.config/opencode/skills/` has the skill directories
- Run `opencode skill list` to verify

### Filesystem MCP "Failed to list files"
- Check `opencode.json` has correct Filesystem path
- Verify the path exists and is accessible
- Restart OpenCode Desktop after config changes

### GitNexus not working
- Run `npx gitnexus analyze` in the workflow directory
- Check GitNexus is running: `ps aux | grep gitnexus`

### SonarQube not accessible
- Check container is running: `docker ps | grep sonarqube`
- Check port mapping: `docker port sonarqube`
- Default URL: http://localhost:9000

## Support

- Workflow repo: https://github.com/marciojusto/workflow
- OpenCode docs: https://opencode.ai/docs
- Kilo Gateway: https://kilo.ai/gateway
