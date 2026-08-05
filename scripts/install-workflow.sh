#!/bin/bash
set -e

# Workflow Installer v2.0.0
# Tool-agnostic, multi-provider, interactive installer

echo "🚀 Workflow Installer v2.0.0"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }
prompt() { echo -e "${BLUE}?${NC} $1"; }

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_REPO="https://github.com/marciojusto/workflow.git"
STATE_FILE="$HOME/.workflow-installer-state.json"
TMP_DIR="/tmp/workflow-installer-$$"

# Ensure tmp dir exists
mkdir -p "$TMP_DIR"

backup_file() {
    local file="$1"
    if [ -f "$file" ]; then
        local backup="${file}.backup.$(date +%Y%m%d-%H%M%S)"
        cp "$file" "$backup"
        info "Backup criado: $backup"
    fi
}

ask_yes_no() {
    local question="$1"
    local default="${2:-n}"
    read -p "$question (s/n) [default: $default]: " answer
    answer="${answer:-$default}"
    [[ "$answer" =~ ^[Ss]$ ]]
}

get_tool_config_dir() {
    case "$1" in
        opencode) echo "$HOME/.config/opencode" ;;
        claude) echo "$HOME/.claude" ;;
        cursor) echo "$HOME/.cursor" ;;
        codex) echo "$HOME/.codex" ;;
        windsurf) echo "$HOME/.windsurf" ;;
        *) echo "" ;;
    esac
}

# ── Step 0: Prerequisites ──
check_prerequisites() {
    echo "Step 0/8: Verificando pré-requisitos..."
    echo ""

    if ! command -v node &> /dev/null; then
        error "Node.js não encontrado. Instale em https://nodejs.org"
    fi
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        error "Node.js >= 18 requerido. Atual: $(node --version)"
    fi
    info "Node.js $(node --version)"

    if ! command -v npm &> /dev/null; then
        error "npm não encontrado"
    fi
    info "npm $(npm --version)"

    if ! command -v git &> /dev/null; then
        error "Git não encontrado. Instale em https://git-scm.com"
    fi
    info "Git $(git --version)"

    if ! command -v python3 &> /dev/null; then
        error "Python3 não encontrado. Instale em https://python.org"
    fi
    info "Python $(python3 --version)"

    if command -v docker &> /dev/null; then
        info "Docker $(docker --version)"
    else
        warn "Docker não encontrado. SonarQube não funcionará."
    fi

    echo ""
    echo "================================"
    echo ""
}

# ── Step 1: Workflow Directory ──
setup_workflow_dir() {
    echo "Step 1/8: Configurando diretório do workflow..."
    echo ""

    # Load existing state if available
    if [ -f "$STATE_FILE" ]; then
        EXISTING_ROOT=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('workflow_root', ''))")

        if [ -n "$EXISTING_ROOT" ] && [ -d "$EXISTING_ROOT" ]; then
            warn "Instalação existente detectada em: $EXISTING_ROOT"
            echo "1. Usar existente (skip)"
            echo "2. Sobrescrever (com backup)"
            echo "3. Cancelar"
            read -p "> " choice
            case "$choice" in
                2)
                    backup_file "$EXISTING_ROOT"
                    rm -rf "$EXISTING_ROOT"
                    ;;
                3)
                    error "Instalação cancelada"
                    ;;
                *)
                    info "Usando instalação existente"
                    WORKFLOW_DIR="$EXISTING_ROOT"
                    echo ""
                    echo "================================"
                    echo ""
                    return
                    ;;
            esac
        fi
    fi

    prompt "Onde deseja instalar o workflow?"
    echo "1. ~/workflow (recomendado)"
    echo "2. ./workflow (diretório atual)"
    echo "3. Outro caminho"
    read -p "> " dir_choice

    case "$dir_choice" in
        1) WORKFLOW_DIR="$HOME/workflow" ;;
        2) WORKFLOW_DIR="$(pwd)/workflow" ;;
        3)
            read -p "Caminho completo: " custom_path
            WORKFLOW_DIR="$custom_path"
            ;;
        *) WORKFLOW_DIR="$HOME/workflow" ;;
    esac

    if [ -d "$WORKFLOW_DIR" ]; then
        warn "Diretório já existe: $WORKFLOW_DIR"
        if ask_yes_no "Sobrescrever?" "n"; then
            backup_file "$WORKFLOW_DIR"
            rm -rf "$WORKFLOW_DIR"
        else
            error "Instalação cancelada"
        fi
    fi

    mkdir -p "$(dirname "$WORKFLOW_DIR")"
    git clone "$WORKFLOW_REPO" "$WORKFLOW_DIR"
    cd "$WORKFLOW_DIR"
    info "Workflow clonado para $WORKFLOW_DIR"

    echo ""
    echo "================================"
    echo ""
}

# ── Step 2: Global Packages ──
install_global_packages() {
    echo "Step 2/8: Instalando pacotes globais..."
    echo ""

    if ! command -v gitnexus &> /dev/null; then
        info "Instalando GitNexus..."
        npm install -g gitnexus
    else
        warn "GitNexus já instalado"
    fi

    if ! command -v playwright &> /dev/null; then
        info "Instalando Playwright..."
        npm install -g @playwright/mcp@latest
        npx playwright install --with-deps chromium
    else
        warn "Playwright já instalado"
    fi

    echo ""
    echo "================================"
    echo ""
}

# ── Step 3: Business Expert ──
setup_business_expert() {
    echo "Step 3/8: Configurando agente de domínio..."
    echo ""

    if ! ask_yes_no "Deseja configurar um agente de domínio customizado?" "n"; then
        info "Saltando configuração de expert (workflow funciona sem)"
        echo ""
        echo "================================"
        echo ""
        return
    fi

    read -p "Nome do agente (ex: finance-expert): " EXPERT_NAME
    read -p "Descrição: " EXPERT_DESC
    read -p "Caminhos de conhecimento (separados por vírgula): " KNOWLEDGE_PATHS
    read -p "Modelo primário (ex: kilogateway/kimi-k2.5): " PRIMARY_MODEL
    read -p "Modelo fallback (ex: openrouter/qwen-3.6-plus): " FALLBACK_MODEL

    TEMPLATE="$WORKFLOW_DIR/agents/business-expert-template.md"
    if [ ! -f "$TEMPLATE" ]; then
        error "Template não encontrado: $TEMPLATE"
    fi

    EXPERT_FILE="$WORKFLOW_DIR/agents/${EXPERT_NAME}.md"
    sed -e "s/{{EXPERT_NAME}}/$EXPERT_NAME/g" \
        -e "s/{{EXPERT_DESCRIPTION}}/$EXPERT_DESC/g" \
        -e "s/{{PRIMARY_MODEL}}/$PRIMARY_MODEL/g" \
        -e "s/{{FALLBACK_MODEL}}/$FALLBACK_MODEL/g" \
        -e "s/{{KNOWLEDGE_PATHS}}/$KNOWLEDGE_PATHS/g" \
        -e "s/{{DOMAIN_SECTIONS}}//g" \
        -e "s/{{RESPONSE_GUIDELINES}}//g" \
        "$TEMPLATE" > "$EXPERT_FILE"

    info "Agente de domínio criado: $EXPERT_FILE"

    # Save expert info to temp file for later state update
    echo "$EXPERT_NAME" > "$TMP_DIR/expert_name"
    echo "$EXPERT_DESC" > "$TMP_DIR/expert_desc"
    echo "$PRIMARY_MODEL" > "$TMP_DIR/expert_model"

    echo ""
    echo "================================"
    echo ""
}

# ── Step 4: AI Coding Tools ──
select_ai_tools() {
    echo "Step 4/8: Selecionando ferramentas de IA..."
    echo ""

    prompt "Quais ferramentas deseja configurar? (números separados por espaço)"
    echo "1. OpenCode"
    echo "2. Claude Code"
    echo "3. Cursor"
    echo "4. Codex"
    echo "5. Windsurf"
    echo "6. Outro"
    read -p "> " -a tool_choices

    local tools=("opencode" "claude" "cursor" "codex" "windsurf")
    SELECTED_TOOLS=()
    for choice in "${tool_choices[@]}"; do
        if [ "$choice" -ge 1 ] && [ "$choice" -le 5 ]; then
            SELECTED_TOOLS+=("${tools[$((choice-1))]}")
        elif [ "$choice" -eq 6 ]; then
            read -p "Nome da ferramenta: " custom_tool
            read -p "Diretório de config: " custom_dir
            SELECTED_TOOLS+=("$custom_tool:$custom_dir")
        fi
    done

    if [ ${#SELECTED_TOOLS[@]} -eq 0 ]; then
        warn "Nenhuma ferramenta selecionada"
        echo ""
        echo "================================"
        echo ""
        return
    fi

    info "Ferramentas selecionadas: ${SELECTED_TOOLS[*]}"

    # Save tools list to temp file
    printf '%s\n' "${SELECTED_TOOLS[@]}" > "$TMP_DIR/selected_tools"

    echo ""
    echo "================================"
    echo ""
}

# ── Step 5: LLM Providers ──
select_llm_providers() {
    echo "Step 5/8: Selecionando providers LLM..."
    echo ""

    prompt "Quais providers deseja configurar? (números separados por espaço)"
    echo "1. Kilo Gateway"
    echo "2. OpenAI"
    echo "3. Anthropic"
    echo "4. Google"
    echo "5. OpenRouter"
    echo "6. Ollama (local)"
    read -p "> " -a provider_choices

    local providers=("kilogateway" "openai" "anthropic" "google" "openrouter" "ollama")
    SELECTED_PROVIDERS=()
    for choice in "${provider_choices[@]}"; do
        if [ "$choice" -ge 1 ] && [ "$choice" -le 6 ]; then
            SELECTED_PROVIDERS+=("${providers[$((choice-1))]}")
        fi
    done

    if [ ${#SELECTED_PROVIDERS[@]} -eq 0 ]; then
        warn "Nenhum provider selecionado"
        echo ""
        echo "================================"
        echo ""
        return
    fi

    info "Providers selecionados: ${SELECTED_PROVIDERS[*]}"

    # For each provider, ask API key and default model
    > "$TMP_DIR/selected_providers"
    for provider in "${SELECTED_PROVIDERS[@]}"; do
        PROV_FILE="$WORKFLOW_DIR/config/providers/${provider}.json"
        if [ ! -f "$PROV_FILE" ]; then
            warn "Provider $provider não encontrado, pulando"
            continue
        fi

        ENV_VAR=$(python3 -c "import json; d=json.load(open('$PROV_FILE')); print(d.get('envVar', ''))")
        if [ -n "$ENV_VAR" ] && [ -z "${!ENV_VAR}" ]; then
            prompt "API key para $provider ($ENV_VAR):"
            read -r api_key
            if [ -n "$api_key" ]; then
                export "$ENV_VAR=$api_key"
                warn "API key definida para esta sessão. Adicione ao .env/.bashrc para persistência."
            fi
        fi

        echo "Modelos disponíveis para $provider:"
        python3 -c "import json; d=json.load(open('$PROV_FILE')); [print(f'  {i+1}) {m[\"name\"]} ({m[\"id\"]})') for i,m in enumerate(d.get('models', []))]"
        read -p "Modelo padrão (número): " model_choice
        DEFAULT_MODEL=$(python3 -c "import json; d=json.load(open('$PROV_FILE')); models=d.get('models',[]); idx=int('$model_choice')-1; print(models[idx]['id'] if 0 <= idx < len(models) else '')")

        echo "$provider=$DEFAULT_MODEL" >> "$TMP_DIR/selected_providers"
    done

    echo ""
    echo "================================"
    echo ""
}

# ── Step 6: Configure Tools ──
configure_tools() {
    echo "Step 6/8: Configurando ferramentas..."
    echo ""

    if [ ! -f "$TMP_DIR/selected_tools" ]; then
        warn "Nenhuma ferramenta selecionada para configurar"
        echo ""
        echo "================================"
        echo ""
        return
    fi

    # Read selected tools
    mapfile -t SELECTED_TOOLS < "$TMP_DIR/selected_tools"

    for tool_entry in "${SELECTED_TOOLS[@]}"; do
        if [[ "$tool_entry" == *":"* ]]; then
            TOOL_NAME="${tool_entry%%:*}"
            TOOL_DIR="${tool_entry##*:}"
        else
            TOOL_NAME="$tool_entry"
            TOOL_DIR=$(get_tool_config_dir "$TOOL_NAME")
        fi

        if [ -z "$TOOL_DIR" ]; then
            warn "Diretório de config desconhecido para $TOOL_NAME, pulando"
            continue
        fi

        info "Configurando $TOOL_NAME em $TOOL_DIR"

        # Create backup if config exists
        CONFIG_FILE=""
        case "$TOOL_NAME" in
            opencode) CONFIG_FILE="$TOOL_DIR/opencode.json" ;;
            claude) CONFIG_FILE="$TOOL_DIR/settings.json" ;;
            cursor) CONFIG_FILE="$TOOL_DIR/settings.json" ;;
            codex) CONFIG_FILE="$TOOL_DIR/config.json" ;;
            windsurf) CONFIG_FILE="$TOOL_DIR/config.json" ;;
        esac

        if [ -n "$CONFIG_FILE" ] && [ -f "$CONFIG_FILE" ]; then
            backup_file "$CONFIG_FILE"
        fi

        mkdir -p "$TOOL_DIR"

        # Generate config based on providers
        case "$TOOL_NAME" in
            opencode)
                info "Gerando opencode.json com providers selecionados..."
                # Read selected providers
                PROVIDERS_JSON="{}"
                if [ -f "$TMP_DIR/selected_providers" ]; then
                    # Build providers config
                    PROVIDERS_JSON=$(python3 << 'PYEOF'
import json
providers = {}
providers_file = open('/tmp/providers_list.txt') if os.path.exists('/tmp/providers_list.txt') else []
PYEOF
)
                fi
                ;;
            *)
                warn "Configuração automática para $TOOL_NAME não implementada ainda"
                ;;
        esac
    done

    echo ""
    echo "================================"
    echo ""
}

# ── Step 6b: Install Global Skills ──
install_global_skills() {
    echo "Step 6b/8: Instalando skills globais no OpenCode..."
    echo ""

    if [[ ! " ${SELECTED_TOOLS[*]} " =~ "opencode" ]]; then
        warn "OpenCode não selecionado, pulando instalação de skills globais"
        echo ""
        echo "=============================="
        echo ""
        return
    fi

    OPENCODE_SKILLS_DIR="$HOME/.config/opencode/skills"
    mkdir -p "$OPENCODE_SKILLS_DIR"

    if [ ! -d "$OPENCODE_SKILLS_DIR/tlc-spec-driven" ]; then
        cp -r "$WORKFLOW_DIR/skills/tlc-spec-driven" "$OPENCODE_SKILLS_DIR/"
        info "tlc-spec-driven instalada globalmente"
    else
        warn "tlc-spec-driven já instalada"
    fi

    if [ ! -d "$OPENCODE_SKILLS_DIR/workflow-implementation" ]; then
        cp -r "$WORKFLOW_DIR/skills/workflow-implementation" "$OPENCODE_SKILLS_DIR/"
        info "workflow-implementation instalada globalmente"
    else
        warn "workflow-implementation já instalada"
    fi

    if [ ! -d "$OPENCODE_SKILLS_DIR/teach" ]; then
        cp -r "$WORKFLOW_DIR/skills/teach" "$OPENCODE_SKILLS_DIR/"
        info "teach instalada globalmente"
    else
        warn "teach já instalada"
    fi

    if [ ! -d "$OPENCODE_SKILLS_DIR/grill-with-docs" ]; then
        mkdir -p "$OPENCODE_SKILLS_DIR/grill-with-docs"
        cat > "$OPENCODE_SKILLS_DIR/grill-with-docs/SKILL.md" << 'EOF'
---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Run a `/grilling` session, using the `/domain-modeling` skill.
EOF
        info "grill-with-docs instalada globalmente"
    else
        warn "grill-with-docs já instalada"
    fi

    echo ""
    echo "=============================="
    echo ""
}

# ── Step 7: Workflow Directories ──
create_workflow_dirs() {
    echo "Step 7/8: Criando diretórios do workflow..."
    echo ""

    WORKFLOW_DIR=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('workflow_root', ''))" 2>/dev/null || echo "$WORKFLOW_DIR")
    prompt "Diretório base do workflow? [default: $WORKFLOW_DIR]"
    read -r custom_base
    BASE_DIR="${custom_base:-$WORKFLOW_DIR}"

    mkdir -p "$BASE_DIR/.specs"/{project,codebase,features,quick,grill}
    mkdir -p "$BASE_DIR/plans"
    mkdir -p "$BASE_DIR/scripts"
    mkdir -p "$BASE_DIR/logs"

    info "Diretórios criados em $BASE_DIR"

    # Save to state
    python3 -c "
import json
state_file = '$STATE_FILE'
with open(state_file) as f:
    state = json.load(f)
state['workflow_dirs'] = '$BASE_DIR'
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)
"

    echo ""
    echo "================================"
    echo ""
}

# ── Step 8: Verify ──
verify_installation() {
    echo "Step 8/8: Verificando instalação..."
    echo ""

    if [ ! -f "$STATE_FILE" ]; then
        error "State file não encontrado: $STATE_FILE"
    fi

    WORKFLOW_DIR=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('workflow_root', ''))")
    if [ -z "$WORKFLOW_DIR" ] || [ ! -d "$WORKFLOW_DIR" ]; then
        error "Workflow directory não encontrado: $WORKFLOW_DIR"
    fi
    info "Workflow directory: $WORKFLOW_DIR"

    # Check business expert
    EXPERT_NAME=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('business_expert', {}).get('name', ''))")
    if [ -n "$EXPERT_NAME" ] && [ -f "$WORKFLOW_DIR/agents/${EXPERT_NAME}.md" ]; then
        info "Business expert: $EXPERT_NAME"
    else
        warn "Business expert: não configurado"
    fi

    # Check tools
    TOOLS=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(' '.join(d.get('tools', {}).keys()))")
    for tool in $TOOLS; do
        TOOL_DIR=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('tools', {}).get('$tool', {}).get('config_dir', ''))")
        if [ -n "$TOOL_DIR" ] && [ -d "$TOOL_DIR" ]; then
            info "Tool configurada: $tool ($TOOL_DIR)"
        else
            warn "Tool: $tool (não verificada)"
        fi
    done

    # Check providers
    PROVIDERS=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(' '.join(d.get('providers', {}).keys()))")
    for provider in $PROVIDERS; do
        PROV_FILE="$WORKFLOW_DIR/config/providers/${provider}.json"
        if [ -f "$PROV_FILE" ]; then
            info "Provider disponível: $provider"
        else
            warn "Provider: $provider (arquivo não encontrado)"
        fi
    done

    echo ""
    echo "================================"
    echo ""
    info "Instalação concluída!"
    echo ""
    echo "Próximos passos:"
    echo "1. Configure API keys no seu shell rc (.bashrc/.zshrc)"
    echo "2. Reinicie a ferramenta de IA para carregar skills/agents"
    echo "3. Teste a instalação"
    echo ""
    echo "Documentação: https://github.com/marciojusto/workflow"
}

# ── Migration Detection ──
detect_and_migrate() {
    echo "🔍 Verificando instalação existente..."
    echo ""

    OLD_OPECODE_DIR="$HOME/.config/opencode"
    if [ -d "$OLD_OPECODE_DIR/skills/tlc-spec-driven" ]; then
        warn "Detectada instalação antiga do OpenCode"
        if ask_yes_no "Deseja migrar para o novo formato?" "s"; then
            info "Migrando instalação..."

            OLD_WORKFLOW=$(find "$HOME/Development" -maxdepth 5 -name "workflow" -type d 2>/dev/null | head -1)
            if [ -n "$OLD_WORKFLOW" ]; then
                info "Workflow antigo: $OLD_WORKFLOW"

                python3 -c "
import json
from datetime import datetime, timezone
state = {
    'version': '2.0.0',
    'workflow_root': '$OLD_WORKFLOW',
    'tools': {
        'opencode': {
            'config_dir': '$OLD_OPECODE_DIR',
            'install_mode': 'copy',
            'config_file': 'opencode.json'
        }
    },
    'providers': {
        'kilogateway': {
            'default_model': 'kimi-k2.5'
        }
    },
    'business_expert': {
        'name': 'miles-expert',
        'description': 'Automotive leasing queries and EU vehicle regulations. Specialized in MMP APIs (Miles/Sofico).',
        'model': 'kilogateway/kimi-k2.5'
    },
    'installed_at': datetime.now(timezone.utc).isoformat()
}
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
                info "Migração concluída. State file criado em $STATE_FILE"
            else
                warn "Workflow antigo não encontrado. Crie o state file manualmente."
            fi
        else
            info "Migração cancelada. Instalação atual preservada."
        fi
    fi

    echo ""
}

# ── Update State File ──
update_state_file() {
    python3 << PYEOF
import json
import os

state_file = "$STATE_FILE"
state = {}

if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)

# Update workflow_root
if 'WORKFLOW_DIR' in globals() and WORKFLOW_DIR:
    state['workflow_root'] = WORKFLOW_DIR

# Update tools
if os.path.exists("$TMP_DIR/selected_tools"):
    with open("$TMP_DIR/selected_tools") as f:
        tools = [line.strip() for line in f if line.strip()]
    state['tools'] = {}
    for tool in tools:
        if ':' in tool:
            name, config_dir = tool.split(':', 1)
        else:
            name = tool
            dirs = {
                'opencode': os.path.expanduser('~/.config/opencode'),
                'claude': os.path.expanduser('~/.claude'),
                'cursor': os.path.expanduser('~/.cursor'),
                'codex': os.path.expanduser('~/.codex'),
                'windsurf': os.path.expanduser('~/.windsurf'),
            }
            config_dir = dirs.get(name, '')
        state['tools'][name] = {
            'config_dir': config_dir,
            'install_mode': 'symlink',
            'config_file': ''
        }

# Update providers
if os.path.exists("$TMP_DIR/selected_providers"):
    with open("$TMP_DIR/selected_providers") as f:
        providers = [line.strip() for line in f if line.strip() and '=' in line]
    state['providers'] = {}
    for prov in providers:
        name, model = prov.split('=', 1)
        state['providers'][name] = {
            'default_model': model
        }

# Update business expert
if os.path.exists("$TMP_DIR/expert_name"):
    with open("$TMP_DIR/expert_name") as f:
        expert_name = f.read().strip()
    with open("$TMP_DIR/expert_desc") as f:
        expert_desc = f.read().strip()
    with open("$TMP_DIR/expert_model") as f:
        expert_model = f.read().strip()
    state['business_expert'] = {
        'name': expert_name,
        'description': expert_desc,
        'model': expert_model
    }

state['version'] = '2.0.0'
state['installed_at'] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

print("State file updated successfully")
PYEOF
}

# ── Main ──
main() {
    # Check if state file exists
    if [ ! -f "$STATE_FILE" ]; then
        detect_and_migrate
    else
        info "State file encontrado: $STATE_FILE"
        if ask_yes_no "Usar configuração existente?" "s"; then
            info "Carregando configuração existente..."
            # Load existing values
            WORKFLOW_DIR=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('workflow_root', ''))")
        else
            warn "Re-configuração iniciada..."
            rm -f "$STATE_FILE"
        fi
    fi

    # Run steps
    check_prerequisites
    setup_workflow_dir
    install_global_packages
    setup_business_expert
    select_ai_tools
    select_llm_providers
    configure_tools
    create_workflow_dirs

    # Update state file with all selections
    update_state_file

    verify_installation

    # Cleanup
    rm -rf "$TMP_DIR"
}

main
