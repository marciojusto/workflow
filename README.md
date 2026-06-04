# Workflow Documentation / Documentação do Workflow

> ⚠️ **Este arquivo substitui o antigo MANUAL.md**

---

## 📁 Estrutura do Projeto / Project Structure

```
workflow/
├── agents/              # Agent definitions (copied from .opencode/agent)
├── docker/              # Docker configuration for SonarQube scanning
│   ├── docker-compose.yml
│   └── scan.sh
├── karpathy/            # Wiki system (knowledge management)
│   ├── raw/             # Source documents (PDFs, OpenAPIs)
│   ├── wiki/            # Generated notes
│   ├── history/         # Historical records
│   └── control/         # index.md, log.md
├── plans/               # Implementation plans
├── scripts/             # Utility scripts (read_excel.py)
├── skills/              # Skill definitions (copied from .opencode/skills)
│   ├── workflow-jira-ticket/
│   ├── playwright-ac-validator/
│   ├── log-analyzer-pro/
│   └── tana-jira-sync/
├── tests/               # E2E test outputs
├── MANUAL_EN.md         # English manual
└── MANUAL_PT.md         # Portuguese manual
```

---

## 📄 Manuais Disponíveis / Available Manuals

| Idioma | Arquivo | Descrição |
|--------|---------|-----------|
| 🇬🇧 English | [MANUAL_EN.md](./MANUAL_EN.md) | Complete workflow documentation in English |
| 🇧🇷 Português | [MANUAL_PT.md](./MANUAL_PT.md) | Documentação completa do workflow em Português |

---

## 🚀 Quick Start / Início Rápido

### English
```bash
# View the workflow flowchart
cat MANUAL_EN.md | grep -A 50 "Workflow Flowchart"
```

### Português
```bash
# Ver o fluxograma do workflow
cat MANUAL_PT.md | grep -A 50 "Fluxo do Workflow"
```

---

## 📊 Models / Modelos

| Agent | Model | Cost |
|-------|-------|------|
| workflow-orchestrator | kilo/qwen/qwen3.6-flash | ~$0.33 |
| wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | ~$0.33 |
| miles-expert | kilo/minimax/minimax-m2.7 | ~$0.53 |
| validator | kilo/stepfun/step-3.5-flash:free | FREE |

---

*Last Updated: 2026-05-02*
*Version: 1.3*