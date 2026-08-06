# Workflow Documentation

> ⚠️ **This file replaces the old MANUAL.md**

---

## 📁 Project Structure

```
workflow/
├── agents/              # Agent definitions
│   ├── workflow-orchestrator.md      # Primary coordinator (session mgmt, logging)
│   ├── miles-expert.md               # Domain expert example
│   ├── coherence-checker.md          # Architecture validation
│   ├── review-plan.md                # Plan review
│   ├── e2e-runner.md                 # E2E test execution
│   ├── wiki-keeper.md                # Knowledge management
│   ├── vision-describer.md           # Image analysis
│   └── business-expert-template.md   # Template for custom experts
├── adapters/            # Tracker adapters
│   └── trackers/        # Jira, Redmine, Mock adapters
├── config/
│   └── providers/       # LLM provider configs
│       ├── kilogateway.json
│       ├── openai.json
│       ├── anthropic.json
│       ├── google.json
│       ├── openrouter.json
│       └── ollama.json
├── docker/              # Docker configuration for SonarQube scanning
├── docs/                # 📚 Documentation (NEW)
│   ├── index.md         # Documentation home
│   ├── architecture/    # Architecture guides
│   ├── guides/          # User guides
│   ├── api/             # API documentation
│   └── reference/       # CLI reference
├── karpathy/            # Wiki system (knowledge management)
├── plans/               # Implementation plans
├── scripts/             # Utility scripts
│   ├── install-workflow.sh
│   ├── Install-Workflow.ps1
│   ├── install-state.py          # Session management (NEW)
│   ├── workflow.py               # Unified CLI (NEW)
│   ├── harness-health-check.py
│   ├── step-log.py               # Logging with session support
│   ├── plan-validator.py         # Plan validation (NEW)
│   ├── snapshot-manager.py       # Snapshots & rollback (NEW)
│   └── update-manuals.py
├── skills/              # Skill definitions
│   ├── workflow-installer/
│   ├── workflow-implementation/
│   ├── workflow-logger/          # Logging skill (NEW)
│   ├── tlc-spec-driven/
│   ├── teach/
│   └── ...
├── tests/               # Test suite (NEW)
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── .specs/              # Specifications
├── .workflow/           # Runtime data
│   ├── history/         # Execution history
│   └── snapshots/       # State snapshots (NEW)
└── README.md
```

---

## 📄 Available Manuals

| Language | File | Description |
|----------|------|-------------|
| 🇬🇧 English | [MANUAL_EN.md](./MANUAL_EN.md) | Complete workflow documentation in English |
| 🇧🇷 Português | [MANUAL_PT.md](./MANUAL_PT.md) | Documentação completa do workflow em Português |

---

## ✨ New Features (v3.0)

### Security Scanning (NEW)
Vulnerability detection for dependencies, secrets, and anti-patterns:
```bash
# Scan for vulnerabilities
python3 scripts/workflow.py security-scan --project-root .

# Create baseline before implementation
python3 scripts/workflow.py security-baseline --project-root . --output baseline.json

# Compare after implementation (detect regressions)
python3 scripts/workflow.py security-compare --project-root . --baseline baseline.json
```

**Detects:**
- Hardcoded secrets (API keys, passwords, tokens)
- SQL injection patterns
- XSS vulnerabilities
- Command injection (eval, exec, os.system)
- Insecure deserialization (pickle)
- SSL verification disabled
- Vulnerable dependencies (npm audit, safety)

### Session Management
Pause, resume, and track workflows with full state persistence:
```bash
python3 scripts/workflow.py session-create MMH-1435 auto
python3 scripts/workflow.py session-pause abc123 "waiting_review"
python3 scripts/workflow.py session-resume abc123
```

### Advanced Plan Validation
LLM-powered plan validation with quality scoring (0-100):
```bash
python3 scripts/workflow.py validate-plan plans/MMH-1435_plan.md \
  --current-ac "User can login" --acs "AC1" "AC2"
# Returns: quality_score, issues, principles validation
```

### Automatic Snapshots & Rollback
Pre-step snapshots with one-command rollback:
```bash
# Create snapshot
python3 scripts/workflow.py snapshot-create abc123 snap1 plans/ src/

# Rollback if something goes wrong
python3 scripts/workflow.py rollback abc123
```

### Unified CLI
Single entry point for all workflow operations:
```bash
python3 scripts/workflow.py status
python3 scripts/workflow.py log-view MMH-1435
python3 scripts/workflow.py snapshot-list abc123
```

### Task Tracker Adapters
Pluggable adapters for Jira, Redmine, GitHub, GitLab:
```json
// ~/.workflow-installer-state.json
{
  "tracker": {
    "type": "jira|redmine|github|gitlab|mock",
    "url": "https://your-tracker.com",
    "apiKey": "your-key"
  }
}
```

## 🚀 Installation

The workflow installer is tool-agnostic and supports OpenCode, Claude Code, Cursor, Codex, Windsurf, and custom AI coding tools.

### Prerequisites

- Node.js >= 18
- npm >= 9
- Git >= 2.30
- Python >= 3.10
- Docker (optional, for SonarQube)

### Quick Start

```bash
# Clone the workflow repository
git clone https://github.com/marciojusto/workflow.git ~/workflow
cd ~/workflow

# Run the interactive installer
bash scripts/install-workflow.sh
```

### Windows

```powershell
git clone https://github.com/marciojusto/workflow.git $HOME\workflow
cd $HOME\workflow
.\scripts\Install-Workflow.ps1
```

### Installation Steps

The installer guides you through 8 sequential steps:

1. **Workflow Directory** — choose where to install the workflow
2. **Global Packages** — install GitNexus, Playwright, SonarQube scanner
3. **Business Expert** (optional) — configure a custom domain expert agent
4. **AI Coding Tools** — select which tools to configure (OpenCode, Claude Code, Cursor, etc.)
5. **LLM Providers** — select which providers to configure (Kilo Gateway, OpenAI, Anthropic, etc.)
6. **Tool Configuration** — generate/update config files for each selected tool
7. **Workflow Directories** — create `.specs/`, `plans/`, `scripts/`, `logs/`
8. **Verification** — check that all components are correctly installed

### State File

The installer creates `~/.workflow-installer-state.json` to track your configuration. This enables:

- Re-running the installer to add/remove tools or providers
- Automatic migration from existing installations
- Dynamic path resolution at runtime

### Re-Execution

You can re-run the installer at any time:

```bash
bash scripts/install-workflow.sh
```

It will detect your existing installation and allow you to modify the configuration.

---

## 🏃 Quick Start After Installation

### For OpenCode

```bash
opencode run "Implement JIRA-9999" --mode=auto
```

### Available Modes

| Mode | Description | JIRA/Redmine | Expert | Teach |
|------|-------------|--------------|--------|------|
| `auto` | Full workflow (planning + execution) | Optional | Optional | Auto-recommended |
| `plan` | Planning only, no code execution | Optional | Optional | Auto-recommended |
| `build` | Execution only, from existing plan | Optional | Optional | No |

---

## 📚 Documentation

Complete documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [docs/index.md](docs/index.md) | Documentation home |
| [docs/guides/getting-started.md](docs/guides/getting-started.md) | Getting started guide |
| [docs/architecture/overview.md](docs/architecture/overview.md) | Architecture overview |
| [docs/reference/cli.md](docs/reference/cli.md) | Complete CLI reference |

### Legacy Manuals

- [MANUAL_EN.md](./MANUAL_EN.md) — Complete workflow documentation in English
- [MANUAL_PT.md](./MANUAL_PT.md) — Documentação completa do workflow em Português

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
python3 -m unittest discover tests/unit -v

# Integration tests
python3 -m unittest tests.integration.test_workflow_integration -v

# All tests
python3 -m unittest discover tests -v
```

**Test Coverage:**
- ✅ 40 unit tests (install-state, step-log, plan-validator, snapshot-manager, security-scanner)
- ✅ 4 integration tests (complete workflow lifecycle)

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM Provider API Keys
export KILO_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-api-key-here"
export ANTHROPIC_API_KEY="your-api-key-here"
export GOOGLE_API_KEY="your-api-key-here"
export OPENROUTER_API_KEY="your-api-key-here"

# Workflow paths (optional, defaults to state file)
export WORKFLOW_ROOT="~/workflow"
export WORKFLOW_CONFIG_DIR="~/.config/opencode"
export WORKFLOW_STATE_FILE="~/.workflow-installer-state.json"
```

---

## 📊 Models

| Agent | Model | Cost |
|-------|-------|------|
| workflow-orchestrator | kilo/qwen/qwen3.6-flash | ~$0.33 |
| wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | ~$0.33 |
| miles-expert | kilo/minimax/minimax-m2.7 | ~$0.53 |
| validator | kilo/stepfun/step-3.5-flash:free | FREE |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🔗 Links

- **Repository**: https://github.com/marciojusto/workflow
- **OpenCode Docs**: https://opencode.ai/docs
- **Kilo Gateway**: https://kilo.ai/gateway

---

*Last Updated: 2026-08-05*
*Version: 3.0*
