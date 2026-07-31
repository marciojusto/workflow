#!/bin/bash
set -e

# Workflow Installer
# Installs the complete workflow stack with all dependencies

echo "🚀 Workflow Installer v1.0.0"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Step 0: Check prerequisites
echo "Step 0/9: Checking prerequisites..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    error "Node.js not found. Install from https://nodejs.org"
fi
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    error "Node.js >= 18 required. Current: $(node --version)"
fi
info "Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    error "npm not found. Install Node.js from https://nodejs.org"
fi
info "npm $(npm --version)"

# Check Git
if ! command -v git &> /dev/null; then
    error "Git not found. Install from https://git-scm.com"
fi
info "Git $(git --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python3 not found. Install from https://python.org"
fi
info "Python $(python3 --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    warn "Docker not found. SonarQube will not work. Install from https://docker.com"
else
    info "Docker $(docker --version)"
fi

echo ""
echo "================================"
echo ""

# Step 1: Clone workflow repository
echo "Step 1/9: Cloning workflow repository..."
WORKFLOW_DIR=~/Development/teamwill/mobilize/workflow

if [ -d "$WORKFLOW_DIR" ]; then
    warn "Workflow directory already exists: $WORKFLOW_DIR"
    read -p "Do you want to overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Installation aborted"
    fi
    rm -rf "$WORKFLOW_DIR"
fi

mkdir -p ~/Development/teamwill/mobilize
git clone https://github.com/marciojusto/workflow.git "$WORKFLOW_DIR"
cd "$WORKFLOW_DIR"
info "Workflow cloned to $WORKFLOW_DIR"

echo ""
echo "================================"
echo ""

# Step 2: Install global npm packages
echo "Step 2/9: Installing global npm packages..."
echo ""

# Install GitNexus
if ! command -v gitnexus &> /dev/null; then
    npm install -g gitnexus
    info "GitNexus installed"
else
    warn "GitNexus already installed"
fi

# Install Playwright MCP
if ! command -v playwright &> /dev/null; then
    npm install -g @playwright/mcp@latest
    npx playwright install --with-deps chromium
    info "Playwright installed"
else
    warn "Playwright already installed"
fi

echo ""
echo "================================"
echo ""

# Step 3: Install SonarQube Scanner
echo "Step 3/9: Installing SonarQube scanner..."
echo ""

SONAR_DIR=~/.local/bin/sonar-scanner
if [ -d "$SONAR_DIR" ]; then
    warn "SonarQube scanner already installed at $SONAR_DIR"
else
    mkdir -p ~/.local/bin
    cd ~/.local/bin
    
    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
        SONAR_URL="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-8.1.0.6389-linux-arm64.zip"
    else
        SONAR_URL="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-8.1.0.6389-linux-x64.zip"
    fi
    
    curl -L -o sonar-scanner.zip "$SONAR_URL"
    unzip -q sonar-scanner.zip
    mv sonar-scanner-* sonar-scanner
    chmod +x sonar-scanner/sonar-scanner
    rm sonar-scanner.zip
    
    info "SonarQube scanner installed at $SONAR_DIR"
fi

echo ""
echo "================================"
echo ""

# Step 4: Configure OpenCode
echo "Step 4/9: Configuring OpenCode..."
echo ""

OPENCODE_DIR=~/.config/opencode
mkdir -p "$OPENCODE_DIR"

# Determine filesystem path based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    FILESYSTEM_PATH="/Users/marcio_oliveira/Development"
else
    FILESYSTEM_PATH="/home/$USER/Development"
fi

# Create or update opencode.json
cat > "$OPENCODE_DIR/opencode.json" << EOF
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
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "$FILESYSTEM_PATH"],
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

info "OpenCode configured at $OPENCODE_DIR/opencode.json"
warn "Remember to set KILO_API_KEY environment variable"

echo ""
echo "================================"
echo ""

# Step 5: Install OpenCode skills
echo "Step 5/9: Installing OpenCode skills..."
echo ""

# Install tlc-spec-driven
if [ -d "$OPENCODE_DIR/skills/tlc-spec-driven" ]; then
    warn "tlc-spec-driven already installed"
else
    cp -r "$WORKFLOW_DIR/skills/tlc-spec-driven" "$OPENCODE_DIR/skills/"
    info "tlc-spec-driven installed"
fi

# Install workflow-implementation
if [ -d "$OPENCODE_DIR/skills/workflow-implementation" ]; then
    warn "workflow-implementation already installed"
else
    cp -r "$WORKFLOW_DIR/skills/workflow-implementation" "$OPENCODE_DIR/skills/"
    info "workflow-implementation installed"
fi

# Install grill-with-docs (optional)
if [ -d "$OPENCODE_DIR/skills/grill-with-docs" ]; then
    warn "grill-with-docs already installed"
else
    mkdir -p "$OPENCODE_DIR/skills/grill-with-docs"
    cat > "$OPENCODE_DIR/skills/grill-with-docs/SKILL.md" << 'EOF'
---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Run a `/grilling` session, using the `/domain-modeling` skill.
EOF
    info "grill-with-docs installed"
fi

# Install agents
if [ -d "$OPENCODE_DIR/agents" ]; then
    warn "Agents directory already exists"
else
    mkdir -p "$OPENCODE_DIR/agents"
fi

cp "$WORKFLOW_DIR/agents/"*.md "$OPENCODE_DIR/agents/" 2>/dev/null || true
info "Agents installed"

echo ""
echo "================================"
echo ""

# Step 6: Create workflow directories
echo "Step 6/9: Creating workflow directories..."
echo ""

mkdir -p "$WORKFLOW_DIR/.specs"/{project,codebase,features,quick,grill}
mkdir -p "$WORKFLOW_DIR/plans"
mkdir -p "$WORKFLOW_DIR/scripts"
mkdir -p "$WORKFLOW_DIR/logs"

info "Workflow directories created"

echo ""
echo "================================"
echo ""

# Step 7: Install in project directories (optional)
echo "Step 7/9: Installing in project directories..."
echo ""

# hyperfront
HF_DIR=~/Development/teamwill/mobilize/hyperfront
if [ -d "$HF_DIR" ]; then
    mkdir -p "$HF_DIR/.claude/skills"
    cp -r "$WORKFLOW_DIR/skills/tlc-spec-driven" "$HF_DIR/.claude/skills/"
    cp -r "$WORKFLOW_DIR/skills/workflow-implementation" "$HF_DIR/.claude/skills/"
    cp "$WORKFLOW_DIR/agents/"*.md "$HF_DIR/" 2>/dev/null || true
    info "Installed in hyperfront"
else
    warn "hyperfront directory not found, skipping"
fi

# deal-bs
DB_DIR=~/Development/teamwill/mobilize/deal-bs
if [ -d "$DB_DIR" ]; then
    mkdir -p "$DB_DIR/.claude/skills"
    cp -r "$WORKFLOW_DIR/skills/tlc-spec-driven" "$DB_DIR/.claude/skills/"
    cp -r "$WORKFLOW_DIR/skills/workflow-implementation" "$DB_DIR/.claude/skills/"
    cp "$WORKFLOW_DIR/agents/"*.md "$DB_DIR/" 2>/dev/null || true
    info "Installed in deal-bs"
else
    warn "deal-bs directory not found, skipping"
fi

echo ""
echo "================================"
echo ""

# Step 8: Verify installation
echo "Step 8/9: Verifying installation..."
echo ""

# Check skills
echo "Checking OpenCode skills..."
if [ -d "$OPENCODE_DIR/skills/tlc-spec-driven" ]; then
    info "tlc-spec-driven installed"
else
    error "tlc-spec-driven NOT installed"
fi

if [ -d "$OPENCODE_DIR/skills/workflow-implementation" ]; then
    info "workflow-implementation installed"
else
    error "workflow-implementation NOT installed"
fi

# Check agents
echo ""
echo "Checking OpenCode agents..."
for agent in workflow-orchestrator miles-expert coherence-checker review-plan e2e-runner vision-describer wiki-keeper validator; do
    if [ -f "$OPENCODE_DIR/agents/$agent.md" ]; then
        info "$agent agent installed"
    else
        warn "$agent agent NOT found"
    fi
done

# Check tools
echo ""
echo "Checking installed tools..."
if command -v gitnexus &> /dev/null; then
    info "GitNexus installed"
else
    warn "GitNexus NOT installed"
fi

if [ -d "$SONAR_DIR" ]; then
    info "SonarQube scanner installed"
else
    warn "SonarQube scanner NOT installed"
fi

echo ""
echo "================================"
echo ""

# Step 9: Post-installation instructions
echo "Step 9/9: Post-installation instructions"
echo ""
echo "================================"
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Set your Kilo API key:"
echo "   export KILO_API_KEY=\"your-api-key-here\""
echo "   Get one at: https://kilo.ai/gateway"
echo ""
echo "2. Configure Git (if not already done):"
echo "   git config --global user.name \"Your Name\""
echo "   git config --global user.email \"your.email@example.com\""
echo ""
echo "3. Start SonarQube (optional):"
echo "   cd $WORKFLOW_DIR/docker"
echo "   docker compose up -d sonarqube"
echo "   Access at: http://localhost:9000 (admin/admin)"
echo ""
echo "4. Restart OpenCode Desktop to load all skills and agents"
echo ""
echo "5. Test the installation:"
echo "   opencode run \"Hello, workflow!\" --model=kilogateway/kimi-k2.5"
echo ""
echo "================================"
echo ""
echo "Documentation: https://github.com/marciojusto/workflow"
echo "Support: Open an issue at https://github.com/marciojusto/workflow/issues"
