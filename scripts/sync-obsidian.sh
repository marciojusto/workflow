#!/bin/bash
# sync-karpathy-obsidian.sh - Sincroniza karpathy wiki com Obsidian
# Usage: ./sync-obsidian.sh

set -e

KARPATHY_WIKI=~/Development/teamwill/mobilize/workflow/karpathy/wiki
PLANS_DIR=~/Development/teamwill/mobilize/workflow/plans
OBSIDIAN_VAULT=~/Obsidian/workflow-wiki

echo "🔄 Sincronizando karpathy wiki com Obsidian..."

# Verificar se Obsidian vault existe
if [ ! -d "$OBSIDIAN_VAULT" ]; then
    echo "❌ Vault do Obsidian não encontrada: $OBSIDIAN_VAULT"
    echo "Criando vault..."
    mkdir -p "$OBSIDIAN_VAULT"
fi

# Criar subdiretórios
mkdir -p "$OBSIDIAN_VAULT/concepts"
mkdir -p "$OBSIDIAN_VAULT/references"
mkdir -p "$OBSIDIAN_VAULT/projects"
mkdir -p "$OBSIDIAN_VAULT/emails"
mkdir -p "$OBSIDIAN_VAULT/conversations"
mkdir -p "$OBSIDIAN_VAULT/manuals"
mkdir -p "$OBSIDIAN_VAULT/plans"

# Criar symlinks para ficheiros (não pastas)
echo "📂 Sincronizando concepts..."
cp -n "$KARPATHY_WIKI/concepts"/* "$OBSIDIAN_VAULT/concepts/" 2>/dev/null || true

echo "📂 Sincronizando references..."
cp -n "$KARPATHY_WIKI/references"/* "$OBSIDIAN_VAULT/references/" 2>/dev/null || true

echo "📂 Sincronizando projects..."
cp -n "$KARPATHY_WIKI/projects"/* "$OBSIDIAN_VAULT/projects/" 2>/dev/null || true

echo "📂 Sincronizando emails..."
cp -n "$KARPATHY_WIKI/emails"/* "$OBSIDIAN_VAULT/emails/" 2>/dev/null || true

echo "📂 Sincronizando conversations..."
cp -n "$KARPATHY_WIKI/conversations"/* "$OBSIDIAN_VAULT/conversations/" 2>/dev/null || true

echo "📂 Sincronizando manuals..."
cp -n "$KARPATHY_WIKI/manuals"/* "$OBSIDIAN_VAULT/manuals/" 2>/dev/null || true

echo "📂 Sincronizando plans..."
cp -n "$PLANS_DIR"/* "$OBSIDIAN_VAULT/plans/" 2>/dev/null || true

echo "✅ Sincronização completa!"
echo ""
echo "📝 Notas sincronizadas:"
echo "   - Concepts: $(ls -1 $KARPATHY_WIKI/concepts/ 2>/dev/null | wc -l) ficheiros"
echo "   - References: $(ls -1 $KARPATHY_WIKI/references/ 2>/dev/null | wc -l) ficheiros"
echo "   - Projects: $(ls -1 $KARPATHY_WIKI/projects/ 2>/dev/null | wc -l) ficheiros"
echo "   - Emails: $(ls -1 $KARPATHY_WIKI/emails/ 2>/dev/null | wc -l) ficheiros"
echo "   - Conversations: $(ls -1 $KARPATHY_WIKI/conversations/ 2>/dev/null | wc -l) ficheiros"
echo "   - Manuals: $(ls -1 $KARPATHY_WIKI/manuals/ 2>/dev/null | wc -l) ficheiros"
echo "   - Plans: $(ls -1 $PLANS_DIR/ 2>/dev/null | wc -l) ficheiros"
echo ""
echo "💡 Para abrir no Obsidian: File → Open Folder as Vault → $OBSIDIAN_VAULT"