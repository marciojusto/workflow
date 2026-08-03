# Workflow Documentation

> ⚠️ **This file replaces the old MANUAL.md**

---

## 📁 Project Structure

```
workflow/
├── agents/              # Agent definitions
│   ├── workflow-orchestrator.md
│   ├── miles-expert.md
│   ├── coherence-checker.md
│   ├── review-plan.md
│   ├── e2e-runner.md
│   ├── wiki-keeper.md
│   ├── vision-describer.md
│   └── business-expert-template.md
├── config/
│   └── providers/       # LLM provider configs
│       ├── kilogateway.json
│       ├── openai.json
│       ├── anthropic.json
│       ├── google.json
│       ├── openrouter.json
│       └── ollama.json
├── docker/              # Docker configuration for SonarQube scanning
│   └── docker-compose.yml
├── karpathy/            # Wiki system (knowledge management)
│   ├── raw/             # Source documents (PDFs, OpenAPIs)
│   ├── wiki/            # Generated notes
│   ├── history/         # Historical records
│   └── control/         # index.md, log.md
├── plans/               # Implementation plans
├── scripts/             # Utility scripts
│   ├── install-workflow.sh
│   ├── Install-Workflow.ps1
│   ├── install-state.py
│   ├── harness-health-check.py
│   ├── step-log.py
│   └── update-manuals.py
├── skills/              # Skill definitions
│   ├── workflow-installer/
│   ├── workflow-implementation/
│   ├── tlc-spec-driven/
│   ├── teach/                  # Explain plans in plain language
│   ├── code-quality-checker/
│   ├── e2e-validator/
│   ├── gitnexus-scan/
│   ├── log-analyzer-pro/
│   ├── release-tickets/
│   ├── tana-jira-sync/
│   └── convert-conversation/
├── tests/               # E2E test outputs
├── MANUAL_EN.md         # English manual
├── MANUAL_PT.md         # Portuguese manual
└── README.md
```

---

## 📄 Available Manuals

| Language | File | Description |
|----------|------|-------------|
| 🇬🇧 English | [MANUAL_EN.md](./MANUAL_EN.md) | Complete workflow documentation in English |
| 🇧🇷 Português | [MANUAL_PT.md](./MANUAL_PT.md) | Documentação completa do workflow em Português |

---

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

## 📋 Manuals

For detailed documentation, see:

- [MANUAL_EN.md](./MANUAL_EN.md) — Complete workflow documentation in English
- [MANUAL_PT.md](./MANUAL_PT.md) — Documentação completa do workflow em Português

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

*Last Updated: 2026-07-31*
*Version: 2.0*
