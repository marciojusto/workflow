# Workflow Documentation

Complete documentation for the AI-powered development workflow.

## Quick Links

- [Getting Started](guides/getting-started.md)
- [Architecture Overview](architecture/overview.md)
- [CLI Reference](reference/cli.md)
- [API Documentation](api/index.md)

## What is This?

This workflow is a comprehensive AI-powered development system that:

1. **Orchestrates** complex implementation tasks across multiple AI agents
2. **Manages** the complete lifecycle from ticket to tested code
3. **Ensures** code quality through automated validation and review
4. **Tracks** progress with detailed logging and session management
5. **Recovers** from errors with automatic snapshots and rollback

## Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Tool Support** | Works with OpenCode, Claude Code, Cursor, Codex, Windsurf |
| **Task Tracker Integration** | Jira, Redmine, GitHub, GitLab, or standalone mode |
| **Session Management** | Pause/resume workflows, checkpointing, history |
| **Advanced Validation** | LLM-powered plan validation with quality scoring |
| **Automatic Snapshots** | Pre-step snapshots with one-command rollback |
| **Structured Logging** | JSON logs with session tracking and metrics |
| **Parallel Execution** | Parallel E2E testing for multiple ACs |
| **Teach Mode** | Auto-generated explanations for complex plans |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    workflow-orchestrator                     │
│                    (Primary Coordinator)                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  wiki-keeper  │    │business-expert│    │ workflow-impl │
│  (Knowledge)  │    │  (Analysis)   │    │ (Execution)   │
└───────────────┘    └───────────────┘    └───────────────┘
                                                  │
                    ┌─────────────────────────────┼──────────┐
                    ▼                             ▼          ▼
            ┌───────────────┐            ┌──────────┐ ┌──────────┐
            │  tlc-spec-    │            │ validator│ │coherence-│
            │  driven       │            │          │ │checker   │
            │  (Planning)   │            │(Testing) │ │(Arch)    │
            └───────────────┘            └──────────┘ └──────────┘
```

## Workflow Phases

### Phase 1: Context Gathering
- Extract ticket from tracker OR gather from grill/spike
- Optional domain expert analysis
- Knowledge base query (wiki-keeper)

### Phase 2: Planning
- SPECIFY: Convert context to spec.md with requirement IDs
- DESIGN: Architecture decisions (if complex)
- Create implementation plan
- Validate plan (quality score ≥ 70)

### Phase 3: Execution
- Human approval gate
- Snapshot before changes
- Execute plan
- Architecture coherence check

### Phase 4: Validation
- Run tests (unit, integration, E2E)
- Code quality checks (SonarQube, linting)
- Generate regression tests

### Phase 5: Completion
- Log history
- Create knowledge notes
- Complete session

## Directory Structure

```
workflow/
├── agents/                 # AI agents (orchestrator, experts, validators)
├── skills/                 # Reusable skills (workflow-impl, tlc-spec-driven, etc.)
├── scripts/                # Python utilities (state, logging, validation, snapshots)
├── adapters/               # Tracker adapters (Jira, Redmine, etc.)
├── tests/                  # Test suite (unit + integration)
├── docs/                   # This documentation
├── plans/                  # Generated implementation plans
├── .specs/                 # Specifications and features
├── .workflow/              # Runtime data (history, traces, snapshots)
└── logs/                   # Execution logs
```

## Getting Started

1. **Install**: Run `bash scripts/install-workflow.sh`
2. **Configure**: Set up API keys and trackers
3. **Run**: Use `opencode run "implement feature X"` or equivalent
4. **Monitor**: Use `python3 scripts/workflow.py status`

See [Getting Started Guide](guides/getting-started.md) for detailed instructions.

## Support

- **Issues**: https://github.com/marciojusto/workflow/issues
- **Discussions**: https://github.com/marciojusto/workflow/discussions
