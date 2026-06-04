---
name: release-tickets
version: v1.0.0
description: Consultar quais tickets Jira (MMH-XXXX) estão em cada release do hyperfront via git local.
---

# Release Tickets

## Inputs
- command (opcional): comando e argumentos (ex: "show 1.6.3", "find MMH-1373", "")

## Output
- result: texto formatado com a resposta

## Config
project_path: ~/Development/teamwill/mobilize/hyperfront

## Instructions

You are a skill for querying release <-> ticket mappings using local git history.
The project is at `~/Development/teamwill/mobilize/hyperfront`.

### Comandos disponíveis

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `list` | Lista todas as releases (tags) com data | `release-tickets list` |
| `show <tag>` | Mostra tickets únicos numa release com descrição | `release-tickets show 1.6.3` |
| `find <ticket>` | Releases que contêm o ticket | `release-tickets find MMH-1373` |
| `diff <tag1> <tag2>` | Tickets em tag2 que não estão em tag1 | `release-tickets diff 1.6.0 1.6.3` |
| `help` | Mostra este menu de ajuda | `release-tickets help` |

### Regras

- Se nenhum comando for passado (input vazio), mostra o help interativamente e pergunta "O que deseja consultar?"
- Sempre valide se a tag existe com `git tag -l <tag>` antes de usar
- Use `--no-merges` para evitar commits de merge e focar nos commits reais de feature
- Extraia o ticket ID e a descrição de cada commit — a descrição é o texto após `[MMH-XXXX]` ou `feature/MMH-XXXX:`
- Agrupe commits por ticket ID e mostre apenas o primeiro commit não-merge de cada ticket
- Commits que mencionam dois tickets (ex: `feature/MMH-1474-1475`) devem listar ambos separadamente
- Ordene os tickets por número (MMH-1000 antes de MMH-2000)
- Ao final de cada consulta, pergunte: "Deseja consultar algo mais? (s/N)"

### Extração de descrição do ticket

Para cada commit não-merge, extraia o ticket e descrição assim:

```
Commit: feature/MMH-1474-1475: adjust registration_date mapping
→ Ticket: MMH-1474, Descrição: adjust registration_date mapping
→ Ticket: MMH-1475, Descrição: adjust registration_date mapping

Commit: [MMH-1357] Duplicate the proposal
→ Ticket: MMH-1357, Descrição: Duplicate the proposal

Commit: feature/MMH-1457: adjust the contract layout and behaviour
→ Ticket: MMH-1457, Descrição: adjust the contract layout and behaviour
```

## Steps

### 1. check-input

Se `command` estiver vazio ou for "help":
  - Use o `question` tool para apresentar opções clicáveis:
    - header: "Release Tickets"
    - question: "Selecione um comando:"
    - options:
      - label: "list" | description: "Lista todas as releases"
      - label: "show" | description: "Mostra tickets numa release (ex: show 1.6.3)"
      - label: "find" | description: "Releases que contêm um ticket (ex: find MMH-1373)"
      - label: "diff" | description: "Diferença entre releases (ex: diff 1.6.0 1.6.3)"
  - Aguarde resposta do usuário e peça os argumentos necessários conforme o comando escolhido

Se `command` tiver conteúdo:
  - Faça o parse: primeiro token = comando, restante = argumentos

### 2. validate-arguments

Conforme o comando:

**list**: sem validação.

**show <tag>**:
  - Verifique se a tag existe: `git -C ~/Development/teamwill/mobilize/hyperfront tag -l <tag>`
  - Se não existir: informe e volte ao passo 1 perguntando novamente

**find <ticket>**:
  - Verifique se o formato é MMH-XXXX (maiúsculo, com hífen)
  - Se inválido: informe e volte ao passo 1

**diff <tag1> <tag2>**:
  - Verifique se ambas tags existem
  - Se alguma não existir: informe e volte ao passo 1

### 3. execute

Execute o comando com `git -C ~/Development/teamwill/mobilize/hyperfront`.

#### list
```bash
git tag --sort=-v:refname --format='%(refname:short) | %(creatordate:short)'
```

Formate como lista:
```
Releases disponíveis:

  1. 1.6.3 - 2026-05-13
  2. 1.6.1 - 2026-05-08
  3. 1.6.0 - 2026-05-07
  ...
```

#### show <tag>

**Encontre o intervalo:**
- Obtenha a tag anterior (mais antiga que a tag atual, baseado em versionamento):
  ```bash
  PREV=$(git -C ~/Development/teamwill/mobilize/hyperfront tag --sort=-v:refname | awk '/^<tag>$/{getline; print}')
  ```
- Se `$PREV` estiver vazio (é a tag mais antiga), use `--root` como range

**Extraia os tickets:**
```bash
git -C ~/Development/teamwill/mobilize/hyperfront log $PREV..<tag> --oneline --no-merges --grep="MMH-" | \
  sed -E 's/^[0-9a-f]+ //' | \
  while IFS= read -r msg; do
    desc=$(echo "$msg" | sed -E 's/\[?MMH-[0-9]+(-[0-9]+)*\]?\s*:?\s*//' | sed -E 's/^feature\///' | sed 's/^[[:space:]]*//')
    mmh_groups=$(echo "$msg" | grep -oE 'MMH-[0-9]+(-[0-9]+)+|MMH-[0-9]+')
    tickets=""
    for group in $mmh_groups; do
      tickets="$tickets $(echo "$group" | grep -oE 'MMH-[0-9]+')"
    done
    for ticket in $tickets; do
      [ -n "$ticket" ] && echo "$ticket|$desc"
    done
  done | sort -t'-' -k2 -n | awk -F'|' '!seen[$1]++{printf "  %d. %s - %s\n", ++c, $1, $2}'
```

Se o resultado for vazio, informe: "Nenhum ticket MMH encontrado nesta release."

Formate como:
```
=== Tickets na release <tag> (desde <prev>) ===

  1. MMH-1000 - Descrição do ticket
  2. MMH-1001 - Outra descrição
  ...

Total: N tickets
```

#### find <ticket>

```bash
i=0
for tag in $(git -C ~/Development/teamwill/mobilize/hyperfront tag --sort=-v:refname); do
  count=$(git -C ~/Development/teamwill/mobilize/hyperfront log "$tag" --oneline --grep="<ticket>" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    i=$((i + 1))
    desc=$(git -C ~/Development/teamwill/mobilize/hyperfront log "$tag" --oneline --no-merges --grep="<ticket>" 2>/dev/null | head -1 | sed -E 's/^[0-9a-f]+ //' | sed -E 's/\[?MMH-[0-9]+(-[0-9]+)*\]?\s*:?\s*//' | sed -E 's/^feature\///' | sed 's/^[[:space:]]*//')
    printf "  %d. %s (%d commits) - %s\n" $i "$tag" $count "$desc"
  fi
done
```

Formate como:
```
=== <ticket> encontrado nas seguintes releases ===

  1. 1.6.3 (3 commits) - Duplicate the proposal
  2. 1.6.1 (2 commits) - Duplicate the proposal
  3. 1.5.8 (1 commit)  - Duplicate the proposal
  ...

Total: 3 releases
```

#### diff <tag1> <tag2>

```bash
git -C ~/Development/teamwill/mobilize/hyperfront log <tag1>..<tag2> --oneline --no-merges --grep="MMH-" | \
  sed -E 's/^[0-9a-f]+ //' | \
  while IFS= read -r msg; do
    desc=$(echo "$msg" | sed -E 's/\[?MMH-[0-9]+(-[0-9]+)*\]?\s*:?\s*//' | sed -E 's/^feature\///' | sed 's/^[[:space:]]*//')
    mmh_groups=$(echo "$msg" | grep -oE 'MMH-[0-9]+(-[0-9]+)+|MMH-[0-9]+')
    tickets=""
    for group in $mmh_groups; do
      tickets="$tickets $(echo "$group" | grep -oE 'MMH-[0-9]+')"
    done
    for ticket in $tickets; do
      [ -n "$ticket" ] && echo "$ticket|$desc"
    done
  done | sort -t'-' -k2 -n | awk -F'|' '!seen[$1]++{printf "  %d. %s - %s\n", ++c, $1, $2}'
```

Formate como:
```
=== Tickets em <tag2> que NÃO estão em <tag1> ===

  1. MMH-1000 - Descrição
  2. MMH-1001 - Descrição
  ...

Total: N tickets
```
