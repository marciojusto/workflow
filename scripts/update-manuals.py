#!/usr/bin/env python3
"""Update manual .md files to reflect generic installer changes."""

import os

MANUALS_DIR = os.path.expanduser(
    "~/Development/teamwill/mobilize/workflow/karpathy/wiki/manuals"
)

PT = os.path.join(MANUALS_DIR, "MANUAL_PT.md")
EN = os.path.join(MANUALS_DIR, "MANUAL_EN.md")
PT_GENERIC = os.path.join(MANUALS_DIR, "MANUAL_PT_GENERIC.md")
EN_GENERIC = os.path.join(MANUALS_DIR, "MANUAL_EN_GENERIC.md")


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_common(content: str) -> str:
    content = content.replace(
        '---\nSPECS_DIR="~/Development/teamwill/mobilize/workflow/.specs"\n',
        '---\nSPECS_DIR="{{SPECS_DIR}}"\n',
    )
    content = content.replace(
        'name: workflow-orchestrator\nversion: v1.0.3\n',
        'name: workflow-orchestrator\nversion: v1.0.4\n',
    )
    content = content.replace(
        'description: "Primary orchestrator agent that coordinates the complete implementation workflow. Supports three operation modes: AUTO (full workflow), PLAN (planning only), and BUILD (execution only from existing plan). Auto-detects project type (frontend/backend) and adapts testing strategy accordingly."',
        'description: "Primary orchestrator agent that coordinates the complete implementation workflow. Supports three operation modes: AUTO (full workflow), PLAN (planning only), and BUILD (execution only from existing plan). Auto-detects project type (frontend/backend) and adapts testing strategy accordingly. Business expert name and paths are loaded from installer state file."',
    )
    content = content.replace(
        'LOG="python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py"',
        'LOG="python3 $WORKFLOW_ROOT/scripts/step-log.py"',
    )
    content = content.replace(
        "python3 ~/Development/teamwill/mobilize/workflow/scripts/harness-health-check.py --preflight",
        "python3 $WORKFLOW_ROOT/scripts/harness-health-check.py --preflight",
    )
    content = content.replace(
        "- Frontend (Nuxt): ~/Development/teamwill/mobilize/hyperfront\n"
        "- Backend (Java): ~/Development/teamwill/mobilize/deal-bs\n"
        "- Backend (Node): detected from project root",
        "- Frontend (Nuxt): detected from project root or $WORKFLOW_ROOT\n"
        "- Backend (Java): detected from project root or $WORKFLOW_ROOT\n"
        "- Backend (Node): detected from project root",
    )
    content = content.replace("@miles-expert", "@$BUSINESS_EXPERT")
    content = content.replace("miles-expert generates plan", "$BUSINESS_EXPERT generates plan")
    content = content.replace("miles-expert)", "$BUSINESS_EXPERT)")
    content = content.replace(
        "1. READ existing plan from ~/Development/teamwill/mobilize/workflow/plans/{ticket_id}.json",
        "1. READ existing plan from $WORKFLOW_ROOT/plans/{ticket_id}.json",
    )
    content = content.replace(
        "`~/Development/teamwill/mobilize/workflow/.specs/features/{ticket_id}/spec.md`",
        "`$SPECS_DIR/features/{ticket_id}/spec.md`",
    )
    content = content.replace(
        "workflow/.specs/grill/{ticket_id_or_topic}/",
        "$SPECS_DIR/grill/{ticket_id_or_topic}/",
    )
    content = content.replace(
        "workflow/.specs/grill/{ticket_id}/",
        "$SPECS_DIR/grill/{jira_ticket_id}/",
    )
    content = content.replace(
        "workflow/.specs/grill/auto-{timestamp}/",
        "$SPECS_DIR/grill/auto-{timestamp}/",
    )
    content = content.replace(
        "- Análise de domínio (miles-expert)",
        "- Análise de domínio ($BUSINESS_EXPERT)",
    )
    return content


def update_pt_specific(content: str) -> str:
    content = content.replace(
        "Plano em `workflow/plans/` ou objecto no output",
        "Plano em `$WORKFLOW_ROOT/plans/` ou objecto no output",
    )
    return content


def update_en_specific(content: str) -> str:
    content = content.replace(
        "Plano em `workflow/plans/` ou objecto no output",
        "Plano em `$WORKFLOW_ROOT/plans/` ou objecto no output",
    )
    return content


def normalize_config_block(config_block: str) -> str:
    return (
        config_block
        .replace("# Load business expert name (fallback to miles-expert for backward compatibility)", "# Load business expert name from installer state file")
        .replace('print(json.load(open(\'$STATE_FILE\')).get(\'business_expert\', {}).get(\'name\', \'miles-expert\'))', 'print(json.load(open(\'$STATE_FILE\')).get(\'business_expert\', {}).get(\'name\', \'\'))')
        .replace("    BUSINESS_EXPERT=\"miles-expert\"\n    WORKFLOW_ROOT=\"~/Development/teamwill/mobilize/workflow\"\n", "")
        .replace("**CRITICAL**: Always load this configuration at the start of every workflow mode. Do not hardcode paths or expert names.", "**CRITICAL**: Always load this configuration at the start of every workflow mode. Do not hardcode paths or expert names. If no business expert is configured, skip domain analysis and proceed directly to SPECIFY.")
    )


def add_config_section(content: str, lang: str = "en") -> str:
    config_block = """## Configuration Loading (REQUIRED)

Before any workflow operation, load configuration from the installer state file:

```bash
STATE_FILE="$HOME/.workflow-installer-state.json"

# Load business expert name from installer state file
if [ -f "$STATE_FILE" ]; then
    BUSINESS_EXPERT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('business_expert', {}).get('name', ''))")
    WORKFLOW_ROOT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('workflow_root', ''))")
fi

# Resolve paths
SPECS_DIR="$WORKFLOW_ROOT/.specs"
SCRIPTS_DIR="$WORKFLOW_ROOT/scripts"
```

**CRITICAL**: Always load this configuration at the start of every workflow mode. Do not hardcode paths or expert names. If no business expert is configured, skip domain analysis and proceed directly to SPECIFY.

---

"""

    config_block = normalize_config_block(config_block)

    if lang == "pt":
        intro = "## Configuração do Ambiente (OBRIGATÓRIO)"
        config_block = config_block.replace("**CRITICAL**:", "**CRÍTICO**:")
    else:
        intro = "## Configuration Loading (REQUIRED)"

    # Remove existing config section if present
    for marker in ["## Configuration Loading (REQUIRED)", "## Configuração do Ambiente (OBRIGATÓRIO)"]:
        start = content.find(marker)
        if start != -1:
            end = content.find("---", start + 4)
            if end != -1:
                content = content[:start] + content[end + 3 :]

    # Insert after front matter
    idx = content.find("---", 4)
    if idx != -1:
        end_idx = content.find("---", idx + 3)
        if end_idx != -1:
            content = content[: end_idx + 3] + "\n\n" + config_block + content[end_idx + 3 :]

    return content


def main():
    for path in [PT, EN, PT_GENERIC, EN_GENERIC]:
        if not os.path.exists(path):
            print(f"Skip missing: {path}")
            continue

        original = read_file(path)
        updated = update_common(original)

        if "PT" in os.path.basename(path):
            updated = update_pt_specific(updated)
            lang = "pt"
        else:
            updated = update_en_specific(updated)
            lang = "en"

        updated = add_config_section(updated, lang)

        if updated != original:
            write_file(path, updated)
            print(f"Updated: {path}")
        else:
            print(f"No changes: {path}")


if __name__ == "__main__":
    main()
