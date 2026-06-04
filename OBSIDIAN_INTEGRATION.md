# Integração Obsidian + Wiki do Workflow

Este guia explica como conectar o Obsidian à wiki mantida pelo agente wiki-keeper.

---

## Estrutura Atual do Karpathy

```
~/Development/teamwill/mobilize/workflow/karpathy/
├── wiki/                     # Notas geradas (obsidian-readable)
│   ├── concepts/             # Conceitos fundamentais
│   ├── references/          # Referências de APIs
│   ├── projects/            # Notas de tickets
│   ├── emails/              # Emails processados (.eml)
│   └── manuals/             # Manuais (MANUAL_EN.md, MANUAL_PT.md)
├── raw/                     # Documentos originais (não editáveis)
│   ├── files/               # PDFs, Excel, emails
│   └── openapi/            # 10 especificações MMP APIs
├── history/                # Registos históricos
└── control/                # index.md, log.md
```

---

## Opções de Integração

### Opção 1: Abrir Diretamente no Obsidian (Recomendado para início)

1. **Abrir Obsidian**
2. **File → Open Folder as Vault**
3. Selecionar: `~/Development/teamwill/mobilize/workflow/karpathy`

**Nota:** Isso abre o karpathy como uma vault separada. Recomendado para leitura apenas.

---

### Opção 2: Criar um Symlink na Vault do Obsidian

Se já tens uma vault do Obsidian:

```bash
# Criar symlink para a pasta wiki
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki ~/path/to/obsidian-vault/karpathy-wiki
```

No macOS pode precisar de:
```bash
# Se o symlink não funcionar, usar uma abordagem alternativa
```

---

### Opção 3: Obsidian Git (Sincronização Automática)

Se quiseres manter a wiki sincronizada automaticamente:

1. **No Obsidian, instalar plugin "Obsidian Git"**
2. **Configurar um clone do repositório** que contenha o karpathy
3. **Configurar backup automático**

No entanto, note-se que o karpathy não está num git repo atualmente.

---

### Opção 4: Obsidian Shell Commands (Mais poderoso)

Instalar [Obsidian Shell Commands](https://github.com/ghostlyshell/obsidian-shell-commands) para:

- Abrir ficheiros diretamente no VS Code
- Executar comandos do workflow
- Criar atalhos para ações comuns

---

## Configuração Recomendada

### steps 1: Criar uma Vault dedicada

Recomendo criar uma vault Obsidian dedicada para o workflow:

1. Criar pasta: `~/Obsidian/workflow-wiki/`
2. Criar subdiretórios que espelham a estrutura do karpathy:
   ```
   ~/Obsidian/workflow-wiki/
   ├── 00-inbox/           # Notas novas/rascunhos
   ├── 10-concepts/        # maps to wiki/concepts
   ├── 20-references/      # maps to wiki/references
   ├── 30-projects/        # maps to wiki/projects
   ├── 40-emails/          # maps to wiki/emails
   ├── 50-manuals/         # maps to wiki/manuals (MANUAL_EN.md, MANUAL_PT.md)
   └── 60-raw/             # maps to raw/files
   ```

### steps 2: Usar symbolic links

```bash
# Criar a vault
mkdir -p ~/Obsidian/workflow-wiki

# Criar symlinks para a wiki do karpathy
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki/concepts ~/Obsidian/workflow-wiki/10-concepts
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki/references ~/Obsidian/workflow-wiki/20-references
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki/projects ~/Obsidian/workflow-wiki/30-projects
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki/emails ~/Obsidian/workflow-wiki/40-emails
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/wiki/manuals ~/Obsidian/workflow-wiki/50-manuals
ln -s ~/Development/teamwill/mobilize/workflow/karpathy/raw/files ~/Obsidian/workflow-wiki/60-raw
```

### steps 3: Abrir no Obsidian

1. Abrir Obsidian
2. File → Open Folder as Vault
3. Selecionar `~/Obsidian/workflow-wiki`

---

## Funcionalidades do Obsidian que podem ser usadas

| Funcionalidade | Uso no Workflow |
|----------------|------------------|
| ** backlinks** | Rastrear conexões entre notas de tickets |
| **Graph view** | Visualizar relações entre conceitos |
| **Tags** | Usar #okta, #party, #offer, etc. |
| **Search** | Buscar em todas as notas |
| **Templates** | Criar notas de tickets |

---

## Regras de Edição

⚠️ **IMPORTANTE:**

1. **Nunca editar ficheiros em `raw/`** - são imutáveis
2. **Editar apenas em `wiki/`** - notas geradas
3. **Usar Obsidian para:**
   - Leitura de notas existentes
   - Adicionar anotações pessoais
   - Criar links entre conceitos
4. **O wiki-keeper pode sobrescrever notas** em `wiki/` quando:
   - Processar novos PDFs
   - Processar novos emails
   - Criar notas de tickets

---

## Scripts Úteis

### Script: Sincronizar com Obsidian

```bash
#!/bin/bash
# sync-karpathy-obsidian.sh

KARPATHY_WIKI=~/Development/teamwill/mobilize/workflow/karpathy/wiki
OBSIDIAN_WIKI=~/Obsidian/workflow-wiki

# Criar estrutura se não existir
mkdir -p $OBSIDIAN_WIKI/{concepts,references,projects,emails}

# Criar symlinks (ignora se já existirem)
ln -sf $KARPATHY_WIKI/concepts/* $OBSIDIAN_WIKI/concepts/ 2>/dev/null || true
ln -sf $KARPATHY_WIKI/references/* $OBSIDIAN_WIKI/references/ 2>/dev/null || true
ln -sf $KARPATHY_WIKI/projects/* $OBSIDIAN_WIKI/projects/ 2>/dev/null || true
ln -sf $KARPATHY_WIKI/emails/* $OBSIDIAN_WIKI/emails/ 2>/dev/null || true

echo "Sincronizado!"
```

---

## Configuração do Obsidian (settings.json)

Para melhor experiência, no Obsidian:

1. **Settings → Files & Links**:
   - Default location for new notes: `30-projects/`
   - New link format: Relative path

2. **Settings → Appearance**:
   - Theme: Minimal ou Dark

3. **Instalar plugins recomendados**:
   - **Obsidian Git** (se usar git)
   - **Quick Add** (para criação rápida)
   - **Templater** (para templates)

---

## Resumo

| Método | Melhor Para |
|--------|-------------|
| **Abrir pasta diretamente** | Leitura rápida, sem config |
| **Symlinks** | Integração completa com Obsidian |
| **Obsidian Git** | Equipa, versionamento |

**Recomendado:** Usar o método "Abrir pasta diretamente" para começar. Se quiseres editingbidirecional, usar symlinks.

---

## Como o wiki-keeper funciona com Obsidian

1. O wiki-keeper cria/editar notas em `karpathy/wiki/`
2. Quando abres no Obsidian, vês as mesmas notas
3. Podes adicionar as tuas próprias notas em `wiki/`
4. **Cuidado:** O wiki-keeper pode sobrescrever notas existentes

**Dica:** Cria notas pessoais com prefixo `_` (ex: `_notas-pessoais.md`) para o wiki-keeper não sobrescrever.