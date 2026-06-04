# Manual do Workflow (Português)

>  Versão: 2.4 | Última Atualização: 2026-05-19

## 1. Visão Geral

Este workflow é um sistema de implementação automatizada para tickets Jira que coordena múltiplos agentes de IA para analisar requisitos, implementar funcionalidades e validar resultados usando testes E2E Playwright.

## 2. Fluxo do Workflow

```
┌─────────────────┐
│ UTILIZADOR      │
│ Fornece ID do   │
│ Ticket Jira     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ workflow-       │
│ orchestrator    │
│ Modelo: deepseek│
│ v4-flash        │
│ Modo: PRIMARY   │
│ Timeout: 10min  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────────┐
│ INÍCIO│ │ INVOC. MANUAL │
│ wiki- │ │ @wiki-keeper  │
│ keeper│ │ @miles-expert │
│ Modelo│ │ @e2e-runner  │
│ qwen  │ └───────────────┘
│ 3.5   │
└──┬────┘
   │
   ▼
┌──────────┐
│ miles-   │
│ expert   │
│ Modelo:  │
│ deepseek │
│ v4-pro   │
│ Timeout: │
│ 15min    │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ workflow-jira-   │
│ ticket (SKILL)   │
│ 8 passos         │
│ Timeout: 30min   │
└──────┬───────────┘
       │
       ▼
┌──────────┐
│ e2e-runner│
│ Modelo:  │
│ Step-3.5 │
│ Flash    │
│ Timeout: │
│ 15min    │
└────┬─────┘
     │
     ▼
┌──────────┐
│ FIM      │
│ wiki-    │
│ keeper   │
│ Cria     │
│ nota do  │
│ ticket   │
└──────────┘
```

## 3. Descrição e Funções dos Agentes

### 3.1 workflow-orchestrator

| Atributo | Valor |
|----------|-------|
| **Nome** | workflow-orchestrator |
| **Versão** | v1.0.3 |
| **Modelo** | opencode/deepseek-v4-flash-free-free |
| **Modelo de Fallback** | kilo/minimax/minimax-m2.7 |
| **Timeout** | 10 minutos |
| **Modo** | **primary** (utilizador invoca diretamente) |
| **Função Principal** | Coordenar o fluxo completo de implementação |

**Responsabilidades:**
- Receber tarefas do utilizador ou IDs de tickets Jira
- Delegar tarefas aos agentes apropriados em sequência
- Gerir tratamento de erros e ciclos de correção
- Solicitar aprovação humana quando necessário
- Manter estado do workflow e rastreabilidade

**Tratamento de Erros:**
1. Se timeout: retry com o mesmo modelo (até ao limite)
2. Se erro de modelo: mudar para fallback
3. Registar o erro no histórico do workflow
4. Se todos os retries esgotados: solicitar intervenção humana

**Comandos de Emergência:**
- `/stop` ou `/cancel`: Cancelar workflow a qualquer momento

**Quando é invocado:**
1. Utilizador fornece tarefa ou ID do ticket Jira
2. Orchestrator inicia o workflow no passo 1 (wiki-keeper)
3. Orchestrator delega ao miles-expert para análise
4. Orchestrator invoca workflow-jira-ticket para implementação
5. Orchestrator delega ao e2e-runner para testes
6. Orchestrator invoca wiki-keeper no FIM para criar notas
7. Se os testes falharem, orchestrator faz loop para miles-expert

### 3.1.1 Modos de Operação do Orchestrator

O workflow-orchestrator suporta três modos de operação:

| Modo | Comando | Descrição |
|------|---------|-----------|
| **Automático** | `auto` | Workflow completo (planejamento + execução) |
| **Plan** | `plan` | Apenas planejamento, sem execução de código |
| **Build** | `build` | Apenas execução, a partir de plano existente |

**Fluxo por modo:**

```
┌─────────────────────────────────────────────────────────┐
│              WORKFLOW ORCHESTRATOR v1.0.2               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Pergunta: "Qual modo? auto/plan/build"                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
    [AUTO]       [PLAN]       [BUILD]      [/STOP]
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │  FULL   │  │ PLAN    │  │ BUILD    │
   │WORKFLOW │  │ ONLY    │  │ ONLY     │
   └─────────┘  └─────────┘  └──────────┘
        │            │            │
        │            ▼            ▼
        │    ┌────────────┐  ┌──────────────┐
        │    │ "Planeja-  │  │ Ler plano    │
        │    │  mento     │  │ de .json     │
        │    │ concluído!│  │              │
        │    │ Digite     │  │ request-     │
        │    │ BUILD"    │  │ human-       │
        │    └────────────┘  │ approval     │
        │                    └──────────────┘
        │                           │
        └──────────┬────────────────┘
                   ▼
         ┌─────────────────┐
         │  E2E-RUNNER   │
         │ + WIKI-KEEPER   │
         └─────────────────┘
```

**Modo AUTO (padrão):**
- Workflow completo: wiki-keeper → miles-expert → workflow-jira-ticket (completo) → e2e-runner → wiki-keeper

**Modo PLAN:**
- wiki-keeper → miles-expert → workflow-jira-ticket (apenas create-plan + validate-plan)
- **Pára aqui** e notifica: "Planejamento concluído. Digite BUILD para continuar"

**Modo BUILD:**
- Lê plano de `.workflow/history/{ticket_id}.json`
- request-human-approval → workflow-jira-ticket (apenas execute-plan) → e2e-runner → wiki-keeper

**Persistência de Planos:**
- Planos são guardados em: `.workflow/history/{jira_ticket_id}.json`
- BUILD mode lê este arquivo para continuar a execução

### 3.2 wiki-keeper

| Atributo | Valor |
|----------|-------|
| **Nome** | wiki-keeper |
| **Versão** | v1.0.1 |
| **Modelo** | kilo/qwen/qwen3.5-flash-02-23 |
| **Modelo de Fallback** | kilo/qwen/qwen3.6-flash |
| **Retry** | 3 |
| **Timeout** | 5 minutos |
| **Modo** | subagent |
| **Função Principal** | Gestão de conhecimento usando o Método Karpathy |

**Capacidade de Leitura de PDF:**
- O wiki-keeper pode ler ficheiros PDF (texto ou imagem)
- Usa `pdftotext` para PDFs com texto selecionável
- Usa `pdftoppm` + `tesseract` (OCR) para PDFs scaneados/imagens
- Requer ferramentas: `poppler` e `tesseract` (via Homebrew)

**Capacidade de Leitura de Email (.eml):**
- O wiki-keeper pode ler ficheiros de email .eml
- Usa a biblioteca `email` do Python para parsing completo
- Processa emails multipart (text/plain + text/html)
- Decodifica headers (From, To, Subject, Date)
- Extrai e limpa conteúdo do body (remove tags HTML)
- Atribui automaticamente tags de domínio: #okta, #party, #offer, #stipulations, #contract, #delivery, #catalog, #general
- Cria notas no diretório `wiki/emails/`
- Processa novos emails automaticamente no início do workflow

**Responsabilidades:**
- Gerir wiki pessoal em formato Markdown
- Consultar conhecimento existente na wiki
- Ingerir novos documentos (PDFs, OpenAPIs, etc.)
- Criar notas de tickets após implementação
- Executar verificação de estado da estrutura da wiki
- Controlar ficheiros processados em control/log.md

**Estrutura da Wiki:**
```
~/Development/teamwill/mobilize/workflow/karpathy/
├── raw/           # Documentos originais imutáveis
├── wiki/          # Notas geradas
│   ├── concepts/   # Conceitos fundamentais
│   ├── references/ # Referências de APIs, documentação
│   └── projects/   # Notas de implementação de tickets
├── history/       # Registos históricos
└── control/       # index.md, log.md
```

### 3.3 miles-expert

| Atributo | Valor |
|----------|-------|
| **Nome** | miles-expert |
| **Versão** | v1.0.2 |
| **Modelo** | kilo/deepseek/deepseek-v4-pro |
| **Modelo de Fallback** | kilo/minimax/minimax-m2.7 |
| **Retry** | 2 |
| **Timeout** | 15 minutos |
| **Modo** | subagent |
| **Função Principal** | Expert em domínio automotive europeu (leasing/financing) |
| **Raciocínio** | mode: all (raciocínio profundo para investigação de bugs e análise de código) |

**Responsabilidades:**
- Análise profunda de tickets Jira (user stories e bugs)
- Identificar APIs MMP afetadas (Miles/Sofico Platform)
- Consultar materiais RAG (especificações OpenAPI, ficheiros locais)
- Fazer perguntas de clarificação antes de prosseguir
- Invocar workflow-jira-ticket para implementação

**Conhecimento de Domínio:**
- 10 APIs MMP: Quotation, Car Quote, Catalog, Dealer POS, Contract, Credit Retail, Customer, Document, Driver, Supplier
- Regulamentos do ciclo de vida de veículos na UE
- Cálculos de IVA e impostos
- Ciclo de vida do contrato: quote → pending → active → terminated

### 3.4 e2e-runner

| Atributo | Valor |
|----------|-------|
| **Nome** | e2e-runner |
| **Versão** | v1.0.3 |
| **Modelo** | kilo/stepfun/step-3.5-flash:free |
| **Modelo de Fallback** | kilo/minimax/minimax-m2.7 |
| **Retry** | 2 |
| **Timeout** | 15 minutos |
| **Modo** | subagent |
| **Função Principal** | Testes E2E com Playwright |

**Responsabilidades:**
- Executar testes E2E com Playwright
- Validar Critérios de Aceitação (AC)
- Capturar screenshots nos pontos-chave
- Fornecer feedback claro de pass/fail
- Incluir contextId no output de erros para debugging

**Diretrizes:**
- Quando login expira: deixar utilizador fazer login novamente
- Quando aparece popup de Data Privacy: clicar "sending by email"
- Quando código postal é necessário: usar 35309
- Botão de fase de proposta ativado após clicar "send secci"

## 4. Tabela de Delegação de Agentes

| Tarefa | Delegar Para | Modelo | Retry | Timeout |
|--------|-------------|--------|-------|----------|
| Gestão de conhecimento (início) | @wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | 3 | 5min |
| Gestão de conhecimento (fim) | @wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | 3 | 5min |
| Análise de domínio profunda (default) | @miles-expert | kilo/minimax/minimax-m2.7 | 2 | 10min |
| Análise de domínio profunda (escalação) | @miles-expert | kilo/deepseek/deepseek-v4-pro | 2 | 15min |
| Revisão independente do plano | @review-plan | kilo/z-ai/glm-5.1 | 2 | 10min |
| Validação de coerência arquitectural | @coherence-checker | kilo/minimax/minimax-m2.7 | 2 | 8min |
| Execução de testes | @e2e-runner | kilo/stepfun/step-3.5-flash:free | 2 | 15min |
| Workflow de implementação | @workflow-jira-ticket | (skill) | 2 | 30min |

### Modelos de Fallback
Se o modelo primário falhar, usar nesta ordem:
1. **wiki-keeper**: kilo/qwen/qwen3.6-flash → kilo/qwen/qwen3.5-flash-02-23
2. **miles-expert**: M2.7 default → V4 Pro escalação (em complexidade/ambiguidade) → V4 Pro fallback (em falha)
3. **e2e-runner**: kilo/minimax/minimax-m2.7 (self-fallback)

### Seleção de Modelo do Miles-Expert
- **Default**: MiniMax M2.7 (204,800 tokens) para complexidade baixa/média, análise single-module
- **Escalação**: DeepSeek V4 Pro (1M tokens) quando: alta ambiguidade, cross-module, muito contexto, alto risco
- **Fallback**: Se M2.7 falhar → escalar para V4 Pro

## 5. Descrição das Skills

### 5.1 workflow-jira-ticket (SKILL)

| Atributo | Valor |
|----------|-------|
| **Nome** | workflow-jira-ticket |
| **Tipo** | Skill (workflow iterativo) |
| **Retry** | 2 |
| **Timeout** | 30 minutos |
| **Purpose** | Implementar tickets Jira AC a AC |

**4 Modos de Operação:**

| Modo | Descrição |
|------|------------|
| `nova` | Implementação completa para story ticket com ACs |
| `bug` | Correção de bug para ticket sem ACs |
| `validar` | Validar branch existente (checklist + screenshots) |
| `continuar` | Continuar implementação incompleta do histórico |

**Auto-Detecção de Tipo de Projeto:**

O workflow detecta automaticamente o tipo de projeto:

| Tipo Detectado | Arquivo Indicador | Framework de Testes | Comando |
|----------------|-------------------|---------------------|---------|
| nuxt-frontend | package.json + playwright.config.ts | Playwright | npx playwright test |
| java-spring-backend | pom.xml + src/test/java | JUnit/Maven | ./mvnw test |
| node-backend | package.json (sem playwright) | Jest/Mocha | npm test |

Caminhos padrão:
- Frontend: ~/Development/teamwill/mobilize/hyperfront
- Backend (Java): ~/Development/teamwill/mobilize/deal-bs
- Backend (Node): detectado a partir da raiz do projeto

**Fluxo Completo:**
0. **mode-selection**: Utilizador seleciona modo (nova/bug/validar/continuar)
0.1 **check-project-guidelines**: Lê AGENTS.md para diretrizes do projeto
0.2 **check-app-running**: Verifica se app está a correr (apenas modo validar)
0.3 **extract-jira-ticket**: Extrair detalhes do ticket, ACs, anexos
0.4 **check-all-done**: Verificar se todas as ACs foram completadas
0.5 **analyze-with-miles-expert** (OBRIGATÓRIO - apenas modos nova/bug/continuar, não validar):
   - Análise profunda do domínio via miles-expert (SEMPRE executado)
   - Input: title, description, ACs, current_ac, project_type
   - Output: domain_analysis, risk_areas, dependencies
   - Usado para informar create-plan, independente da complexidade

**Modo Validar (1):**
1. **validate-branch**: Executa e2e-validator com todas ACs → cria relatório wiki → STOP

**Modos Nova/Bug (2-10):**
2. **check-existing-plan**: Verificar se plano já existe
3. **create-plan**: Gerar plano de implementação para AC atual
4. **validate-plan**: Validar correção do plano (2 retries)
5. **request-human-approval**: **OBRIGATÓRIO** - Obter aprovação antes de executar
   - CRITICAL: NENHUMA alteração de código pode ser feita antes de approved == true
6. **execute-plan**: Implementar o código (SÓ APÓS approved == true)
7. **e2e-validator**: Executar testes E2E (chama agente e2e-runner)
7.5 **generate-regression-test**: Gerar teste de regressão automático após validação
   - Copia template para `playwright/tests/regression/{ticket_id}_ac{index}.spec.ts`
   - Inclui fluxo completo do ticket e asserções do validator
   - Executado automaticamente no step 8c
8. **review-implementation**: Revisar alterações de código (2 retries)
8b. **code-quality-checker**: Verificar princípios de código (DRY, KISS, YAGNI, SOLID, SoC) E executar SonarQube automaticamente
8c. **run-regression-tests**: Executar testes de regressão
8d. **log-history**: Atualizar histórico de implementação → próxima AC

### 5.2 e2e-validator (SKILL)

| Atributo | Valor |
|----------|-------|
| **Nome** | e2e-validator |
| **Versão** | v1.0.1 |
| **Tipo** | Skill (validação) |
| **Purpose** | Testar critérios de aceitação usando Playwright |

**Inputs:**
- current_ac: O AC a validar
- scope: "current_only" ou "all"
- app_url: URL da aplicação alvo (default: http://localhost:3000)

**Outputs:**
- passed: Booleano
- screenshot_path: Caminho para screenshot
- error_message: Descrição do erro se falhou
- contextId: Identificador de debug

### 5.3 Verificação de Princípios de Código

Durante o step **review-implementation**, o workflow verifica automaticamente os princípios de código E executa SonarQube:

| Princípio | Frontend (Nuxt/Vue) | Backend (Java/Spring) |
|-----------|---------------------|----------------------|
| **DRY** | Duplicated logic → extract to composables | Duplicated code → extract to services |
| **SoC** | API calls via bsClient (NOT direct fetch) | Proper layer separation (controller → service → repository) |
| **KISS** | Functions < 50 lines | Methods < 30 lines |
| **YAGNI** | No unused imports | No unused imports/methods |
| **SOLID** | Component responsibility | DI, single responsibility per class |

**Arquivo de Referência:**
- Frontend: `hyperfront/AGENTS.md`
- Backend: `deal-bs/AGENTS.md`

**Step: review-implementation → step 2.5 verify-code-principles (code-quality-checker v1.0.1)**
- Verifica princípios automaticamente após código usage check
- Se violações encontradas → aprova = false, feedback com problemas
- Se todos princípios seguem → aprova = true

### 5.4 Skills que Podem Ser Invocadas Independentemente

Todas as skills podem ser chamadas diretamente via `call: skill.nome-da-skill`, sem passar pelo workflow-jira-ticket. Isso permite uso modular para tarefas específicas.

#### 5.4.1 e2e-validator

| Atributo | Valor |
|----------|-------|
| **Nome** | e2e-validator |
| **Versão** | v1.0.1 |
| **Quando usar** | "test this AC", "test E2E", "check UI", "validate implementation" |
| **Auto-detecção** | NÃO - requer inputs explícitos |

**Inputs:**
- `current_ac`: Critério de aceitação a testar
- `scope`: "current_only" ou "all"
- `app_url`: URL da app (opcional, default: http://localhost:3000)

**Exemplo de Chamada:**
```yaml
- call: skill.e2e-validator
  input:
    - current_ac: "User can see deal status as approved"
    - scope: "current_only"
    - app_url: "http://localhost:3000"
```

#### 5.4.2 code-quality-checker

| Atributo | Valor |
|----------|-------|
| **Nome** | code-quality-checker |
| **Versão** | v1.0.1 |
| **Quando usar** | "check code principles", "verify DRY", "check SoC", "code review", "run sonar", "sonar scan" |
| **Auto-detecção** | SIM - detecta project_type se não informado |

**Inputs:**
- `files_modified`: Lista de arquivos alterados
- `project_type`: "nuxt-frontend" | "java-spring-backend" | "node-backend" | "auto" (default: auto)
- `base_path`: Caminho do projeto (opcional)
- `scope`: "full" | "quick" (default: quick)
- `run_sonar`: boolean (default: true)
- `sonar_url`: URL do SonarQube (default: http://localhost:9002)
- `sonar_token`: Token de autenticação (default: pré-gerado)

**Exemplo de Chamada:**
```yaml
- call: skill.code-quality-checker
  input:
    - files_modified: ["src/components/DealStatus.vue", "server/api/deals.ts"]
    - project_type: "nuxt-frontend"
    - base_path: "/Users/marcio_oliveira/Development/teamwill/mobilize/hyperfront"
    - run_sonar: true
```

**Chamada Independente (sem project_type):**
```yaml
- call: skill.code-quality-checker
  input:
    - files_modified: ["src/components/DealStatus.vue"]
    - project_type: "auto"  # Detecta automaticamente via pom.xml/package.json
```

#### 5.4.3 log-analyzer-pro

| Atributo | Valor |
|----------|-------|
| **Nome** | log-analyzer-pro |
| **Versão** | v1.0.0 |
| **Quando usar** | "analyze logs", "check errors", "debug issue" |
| **Auto-detecção** | NÃO - requer inputs explícitos |

**Inputs:**
- `log_path`: Caminho para o arquivo de log
- `search_pattern`: Padrão de busca (opcional)
- `error_only`: boolean (opcional)

#### 5.4.4 tana-jira-sync

| Atributo | Valor |
|----------|-------|
| **Nome** | tana-jira-sync |
| **Versão** | v1.0.0 |
| **Quando usar** | "sync to Tana", "create Tana node", "Jira to Tana" |
| **Auto-detecção** | NÃO - requer inputs explícitos |

**Inputs:**
- `jira_ticket_id`: ID do ticket Jira
- `workspace`: Workspace do Tana (opcional)

#### 5.4.5 workflow-jira-ticket

| Atributo | Valor |
|----------|-------|
| **Nome** | workflow-jira-ticket |
| **Versão** | v1.0.5 |
| **Quando usar** | Implementação completa de ticket Jira |
| **Auto-detecção** | SIM - detecta project_type automaticamente |

**Nota:** Esta é a skill principal do workflow. Pode ser chamada independentemente, mas é mais comum ser invocada pelo workflow-orchestrator ou @miles-expert.

### 5.4.6 tlc-spec-driven

| Atributo | Valor |
|----------|-------|
| **Nome** | tlc-spec-driven |
| **Tipo** | Skill (especificação + design) |
| **Fonte** | Tech Lead's Club (agent-skills.techleads.club) |
| **Quando usar** | Especificação estruturada para tickets Jira, após coleta de dados |
| **Auto-detecção** | SIM - ajusta profundidade pela complexidade |

**Integração Híbrida:**
- Fase **SPECIFY** sempre executa após análise miles-expert → gera `spec.md` com IDs de requisitos
- Fase **DESIGN** auto-ajusta (skipped para alterações simples, executa só para Large/Complex)
- workflow-jira-ticket usa os requirement IDs do spec.md para rastreabilidade no create-plan

**Localização:** `workflow/skills/tlc-spec-driven/SKILL.md`

**Ficheiros de referência:** brownfield-mapping.md, specify.md, design.md, implement.md, validate.md, tasks.md, session-handoff.md, quick-mode.md

**Inputs:**
- `jira_ticket_id`: ID do ticket Jira
- `mode`: "nova" | "bug" | "validar" | "continuar"

### 5.5 Resumo: Como Invocar Skills Independentemente

| Sintaxe | Tipo | Exemplo |
|---------|------|---------|
| `call: skill.nome` | Skill (dentro de workflow) | `call: skill.e2e-validator` |
| `@agente` | Agente (invocação direta) | `@wiki-keeper` |

**Nota Importante:**
- Skills são invocadas com `call: skill.nome` **dentro de um workflow ou skill**
- Agentes são invocados com `@agente` **diretamente pelo utilizador**
- A skill `code-quality-checker` pode auto-detectar o tipo de projeto se chamada independentemente

### 5.6 Quando Usar Skill vs Agente

Esta seção explica quando é preferível invocar uma **skill** isoladamente versus um **agente** diretamente.

#### Resumo: Skill vs Agente

| Aspecto | Skill | Agente |
|---------|-------|--------|
| **Invocação** | `call: skill.nome` | `@agente` |
| **Contexto** | Dentro de workflow/skill | Direto pelo utilizador |
| **Abstração** | Maior (inclui guidelines) | Menor (prompt direto) |
| **Complexidade** | Workflows multi-step | Tarefas simples/diretas |
| **Exemplo** | `call: skill.e2e-validator` | `@wiki-keeper` |

#### Quando Usar SKILL (Recomendado)

Use skills quando:

| Cenário | Skill Recomendada | Motivo |
|---------|-------------------|--------|
| Testar ACs de um ticket | `skill.e2e-validator` | Já inclui guidelines (login, postal code, etc) |
| Verificar princípios de código | `skill.code-quality-checker` | Auto-detecta project_type, executa SonarQube |
| Análise completa de ticket Jira | `skill.workflow-jira-ticket` | Fluxo completo com aprovação humana |
| Especificação estruturada | `skill.tlc-spec-driven` | SPECIFY + DESIGN com auto-sizing e IDs de requisitos |
| Analisar logs de erros | `skill.log-analyzer-pro` | Parsing e filtering automático |
| Sincronizar para Tana | `skill.tana-jira-sync` | Integração direta com Jira + Tana |

**Vantagens das Skills:**
- Já incluem guidelines e configurações
- Auto-detecção de parâmetros quando disponíveis
- Workflows otimizados para tarefas específicas
- Menos necessidade de especificar detalhes no prompt

#### Quando Usar AGENTE (Recomendado)

Use agentes diretamente quando:

| Cenário | Agente | Motivo |
|---------|--------|--------|
| Consultar conhecimento na wiki | `@wiki-keeper` | Query simples, sem workflow complexo |
| Perguntas de domínio automotive | `@miles-expert` | Análise direta, sem implementação |
| Tarefas administrativas | `@workflow-orchestrator` | Quando precisa de controle manual do fluxo |

**Vantagens dos Agentes:**
- Mais flexibilidade no prompt
- Resposta direta sem overhead de workflow
- Ideal para perguntas rápidas ou tarefas simples

#### Fluxo de Decisão

```
Preciso fazer uma tarefa...
         │
         ▼
┌─────────────────────────┐
│ É uma tarefa complexa   │
│ com múltiplos steps?    │
└────────┬────────────────┘
         │
    ┌────┴────┐
    SIM      NÃO
    │         │
    ▼         ▼
┌──────────┐ ┌─────────────────┐
│ USE      │ │ USE AGENTE      │
│ SKILL    │ │ DIRETAMENTE     │
└──────────┘ └─────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ Qual tipo de tarefa?                │
├─────────────┬─────────────┬─────────┤
│ Testar AC   │ Code review │ Ticket  │
│ e2e-validator│ code-quality-│workflow-│
│             │ checker     │jira-ticket│
└─────────────┴─────────────┴─────────┘
```

#### Exemplo Prático

**Cenário:** Você quer testar se um AC foi implementado corretamente.

| Opção | Como Fazer | Resultado |
|-------|------------|-----------|
| **Skill (Recomendado)** | `call: skill.e2e-validator` com inputs | Já inclui guidelines de login, postal code, popup privacy |
| **Agente** | `@e2e-runner` com prompt | Requer especificar guidelines no prompt |

**Conclusão:** Para testar ACs, **use a skill** porque ela já sabe as diretrizes (login, postal code 35309, etc). Para perguntas simples à wiki, **use o agente** diretamente.

## 6. Os Agentes Podem Ser Invocados Individualmente?

**SIM** - Todos os agentes podem ser invocados diretamente sem passar pelo workflow-orchestrator.

### 6.1 Exemplos de Invocação Direta

**@wiki-keeper:**
```
Invoca @wiki-keeper para verificar se temos conhecimento sobre a API de Quotation
```

**@miles-expert:**
```
Analisa o ticket Jira MMH-1435 e identifica as APIs afetadas
```

**@e2e-runner:**
```
Valida o AC: "User can see deal status as approved after credit approval"
```

### 6.2 Exemplos de Prompts para Agentes Individuais

#### Prompts do Wiki-keeper:

| Exemplo | Prompt |
|---------|--------|
| Consultar conhecimento | "O que sabemos sobre a Quotation API?" |
| Health check | "Executa uma verificação de estado da wiki" |
| Ingerir novo documento | "Ingerir a nova especificação OpenAPI para miles-contract-v2" |
| Criar nota de ticket | "Criar uma nota de ticket para a implementação do MMH-1435" |

#### Prompts do Miles-expert:

| Exemplo | Prompt |
|---------|--------|
| Analisar ticket | "Analisa o ticket Jira MMH-1435: Create quote workflow" |
| Identificar APIs | "Quais APIs MMP são afetadas pela funcionalidade de seleção de veículo?" |
| Perguntas de clarificação | "Tenho perguntas sobre o tratamento de IVA para frotas multi-país" |

#### Prompts do e2e-runner:

| Exemplo | Prompt |
|---------|--------|
| Testar AC único | "Testar AC: User can see deal status as approved" |
| Testar todas ACs | "Executar todas as ACs para o ticket MMH-1435" |
| Debug | "Testar AC com contextId DEV-12345-67890" |

## 7. Os Agentes Podem Ser Invocados Sem Prompt?

**PARCIALMENTE** - Os agentes requerem alguma forma de input, mas podem ser invocados com contexto mínimo:

| Agente | Input Mínimo | Pode Trabalhar Sem Prompt Explícito? |
|-------|---------------|--------------------------------------|
| workflow-orchestrator | ID do Ticket Jira ou descrição da tarefa | SIM - basta fornecer ID do ticket |
| wiki-keeper | Tipo de ação (query/ingest/health check) | SIM - ações implícitas |
| miles-expert | ID do ticket ou questão de domínio | PRECISA contexto - não funciona sem input |
| e2e-runner | AC para testar | PRECISA AC - não pode validar nada |
| workflow-jira-ticket | ID do Ticket Jira | PRECISA ticket - requer input estruturado |

**Conclusão:** O workflow-orchestrator pode funcionar apenas com um ID de ticket. Outros agentes precisam de mais contexto mas o sistema foi desenhado para fornecer contexto automaticamente através do workflow.

## 8. Tratamento de Erros e Recuperação

### 8.1 Quando um Agente Falha:
1. Verificar se é timeout ou erro de modelo
2. Se timeout: retry com o mesmo modelo (até ao limite)
3. Se erro de modelo: mudar para modelo fallback
4. Registar o erro no histórico do workflow
5. Se todos os retries esgotados: solicitar intervenção humana

### 8.2 Rate Limiting
- Cada agente tem limites de requests por minuto
- Se rate limited: esperar 30s antes de retry
- Se persistente: escalar para humano

### 8.3 Paragem de Emergência
Para cancelar o workflow a qualquer momento, o utilizador pode escrever: `/stop` ou `/cancel`
- O agente atual vai terminar gracefulmente
- O progresso será registado para resume posterior
- O utilizador será notificado do estado incompleto

## 9. GitNexus - Inteligência de Código

O GitNexus fornece capacidades de análise profunda de código para o workflow. Ele cria um grafo de conhecimento da sua base de código, permitindo análise de blast radius, rastreamento de dependências e pesquisa semântica de código.

### 9.1 Instalação e Configuração

```bash
# Instalar CLI globalmente
npm install -g gitnexus

# Indexar repositórios (executar a partir de cada raiz de repo)
cd ~/Development/teamwill/mobilize/hyperfront && npx gitnexus analyze
cd ~/Development/teamwill/mobilize/deal-bs && npx gitnexus analyze

# Iniciar servidor local com UI web
gitnexus serve
```

**UI Web:** http://localhost:4747

### 9.2 Configuração MCP

O GitNexus é configurado via `~/.config/opencode/opencode.json`:

```json
{
  "mcp": {
    "GitNexus": {
      "type": "local",
      "command": ["npx", "-y", "opencode-gitnexus"],
      "enabled": true
    }
  }
}
```

### 9.3 Ferramentas Disponíveis

| Ferramenta | Finalidade |
|------------|------------|
| `gitnexus_query` | Pesquisa semântica no código |
| `gitnexus_context` | Vista 360° de símbolo com refs e participação em processos |
| `gitnexus_impact` | Análise de blast radius com agrupamento por profundidade |
| `gitnexus_detect_changes` | Análise de impacto git-diff |
| `gitnexus_rename` | Rename coordenado multi-arquivo |
| `gitnexus_cypher` | Queries Cypher directas ao grafo |

### 9.4 Uso no Workflow

O GitNexus é **OPCIONAL** e é invocado pelo miles-expert após o passo 0.5 (analyze-with-miles-expert):

```
passo 0.5: analyze-with-miles-expert (OBRIGATÓRIO)
          │
          ▼
    miles-expert avalia:
    "Devo sugerir gitnexus-scan?"
          │
          ▼
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
NÃO USAR            USAR + PERGUNTAR
(simple)          "Deseja executar
                   gitnexus-scan?"
                       │
                       ▼
            ┌─────────┴─────────┐
            │                   │
            ▼                   ▼
      create-plan          GITNEXUS-SCAN
      (basic only)         → contexto melhorado
```

### 9.5 Heurística para Sugestão

**Usar GitNexus quando:**
- Impacto multi-módulo detectado (afeta >1 cluster)
- Bug com causa raiz não óbvia
- Refactoring de mudanças estruturais
- Baixa familiaridade com zona de código
- Necessidade de blast radius antes do planejamento
- Alto risco de regressão

**Não usar quando:**
- Mudança pequena e localizada
- Área claramente conhecida
- Ticket simples, isolado, baixo risco

### 9.6 Skill gitnexus-scan

| Atributo | Valor |
|----------|-------|
| **Nome** | gitnexus-scan |
| **Tipo** | Skill (opcional) |
| **Localização** | `workflow/skills/gitnexus-scan/SKILL.md` |
| **Quando** | Após passo 0.5, antes de create-plan |

**Input:**
- project_type (hyperfront | deal-bs)
- jira_ticket_id
- domain_analysis (do miles-expert)
- risk_areas

**Output:**
- impact_analysis (ficheiros primários/secundários, blast_radius)
- symbol_analysis (símbolos centrais, call chains)
- recommendations (ficheiros para rever, testes para verificar)

### 9.7 Diretórios Chave

| Diretório | Finalidade |
|-----------|------------|
| `~/.gitnexus/registry.json` | Registo global de repos indexados |
| `.gitnexus/` (em cada repo) | Armazenamento local do índice |
| `hyperfront/.gitnexus/` | Índice do hyperfront |
| `deal-bs/.gitnexus/` | Índice do deal-bs |

### 9.8 Notas Importantes

- **TODOS os dados são LOCAIS** - sem cloud, sem APIs externas
- O índice deve ser atualizado após mudanças maiores: `gitnexus analyze --force`
- UI Web auto-detecta servidor local em http://localhost:4747

---

## 10. Estrutura de Diretórios

```
~/Development/teamwill/mobilize/workflow/
├── agents/              # Definições dos agentes
├── docker/              # Configuração Docker para scanning SonarQube
│   ├── docker-compose.yml
│   ├── scan-hyperfront.sh   # SonarQube para projetos frontend (Nuxt/Vue/Node)
│   └── scan-deal-bs.sh      # SonarQube para projetos Java (deal-bs)
├── karpathy/            # Sistema de wiki
│   ├── control/          # index.md, log.md
│   ├── history/          # Registos históricos de implementação
│   ├── raw/              # Documentos fonte
│   │   ├── files/        # PDFs, ficheiros de dados (MMH_1435, MMH_1465)
│   │   └── openapi/      # 10 especificações de API MMP
│   └── wiki/             # Notas geradas
│       ├── concepts/     # Notas de conceitos
│       ├── references/   # Referências de APIs
│       ├── projects/    # Notas de implementação de tickets
│       └── emails/       # Notas de emails processados (.eml)
├── plans/                # Planos de implementação
├── scripts/              # Scripts utilitários
│   └── read_excel.py     # Ler ficheiros Excel do RAG
├── .specs/              # Artefactos spec-driven (tlc-spec-driven)
│   ├── project/          # PROJECT.md, ROADMAP.md, STATE.md
│   ├── codebase/         # Brownfield mapping (STACK, ARCH, CONVENTIONS, etc.)
│   ├── features/         # Specs de funcionalidades com IDs de requisitos
│   └── quick/            # Docs de tarefas ad-hoc
├── skills/              # Definições das skills
│   ├── workflow-jira-ticket/      # Workflow principal de implementação
│   ├── analyze-with-miles-expert/ # Passo 0.5 (OBRIGATÓRIO)
│   ├── tlc-spec-driven/           # Especificação + design (híbrido)
│   ├── e2e-validator/            # Testar ACs
│   ├── code-quality-checker/     # DRY, SOLID, SonarQube
│   ├── log-analyzer-pro          # Análise de logs
│   ├── tana-jira-sync            # Jira → Tana
│   └── gitnexus-scan             # Análise de código (OPCIONAL)
├── tests/               # Outputs de testes E2E
├── MANUAL_EN.md         # Manual em Inglês
└── MANUAL_PT.md         # Manual em Português
```

### Scripts Principais

| Script | Finalidade |
|--------|------------|
| `scripts/read_excel.py` | Ler ficheiros Excel do RAG |
| `docker/scan-hyperfront.sh` | Executar SonarQube para projetos frontend |
| `docker/scan-deal-bs.sh` | Executar SonarQube para projetos Java |
| `docker/docker-compose.yml` | Configuração do container SonarQube |

## 11. Hierarquia Completa Resumo

### Agentes (4)

| # | Agente | Modelo | Versão | Modo | Timeout |
|---|--------|--------|--------|------|---------|
| 1 | workflow-orchestrator | deepseek-v4-flash-free | v1.0.3 | primary | 10min |
| 2 | wiki-keeper | deepseek-v4-flash-free | v1.0.3 | subagent | 5min |
| 3 | miles-expert | minimax-m2.7 / V4 Pro | v1.1.0 | subagent | 10min |
| 4 | review-plan | kilo/z-ai/glm-5.1 | v1.0.0 | subagent | 10min |
| 5 | coherence-checker | minimax-m2.7 | v1.0.0 | subagent | 8min |
| 6 | e2e-runner | step-3.5-flash | v1.0.3 | subagent | 15min |

### Skills (8)

| # | Skill | Tipo | Quando Usada |
|---|-------|------|--------------|
| 1 | workflow-jira-ticket | Workflow principal | Implementação |
| 2 | analyze-with-miles-expert | Passo 0.5 | Modos nova/bug/continuar (OBRIGATÓRIO) |
| 3 | tlc-spec-driven | Spec + Design | Após passo 0.5, SPECIFY + DESIGN |
| 4 | e2e-validator | Validação | Testar ACs |
| 5 | code-quality-checker | Qualidade | DRY, SOLID, SonarQube |
| 6 | log-analyzer-pro | Debug | Análise de logs |
| 7 | tana-jira-sync | Integração | Jira → Tana |
| 8 | gitnexus-scan | Opcional | Após passo 0.5 (OPCIONAL) |

### Passos do workflow-jira-ticket

```
0.  mode-selection
0.1 check-project-guidelines
0.2 check-app-running (apenas modo validar)
0.3 extract-jira-ticket
0.4 check-all-done
0.5 analyze-with-miles-expert (OBRIGATÓRIO - nova/bug/continuar)
    → Opcional: gitnexus-scan (se miles-expert sugerir + utilizador aceitar)
0.6 spec-driven-planning (tlc-spec-driven — híbrido)
    → SPECIFY: .specs/features/{ticket_id}/spec.md
    → DESIGN: .specs/features/{ticket_id}/design.md (Large/Complex apenas)

1.  validate-branch (modo validar)

2.  check-existing-plan
3.  create-plan (com requirement IDs do spec.md)
4.  validate-plan
5.  request-human-approval (OBRIGATÓRIO)
6.  execute-plan
7.  e2e-validator
7.5 generate-regression-test (trace-to-playwright.py se test_trace disponível)
8.  review-implementation
8b. code-quality-checker
8c. run-regression-tests
8d. log-history
```

### Tags de Domínio para Email

| Tag | Domínio |
|-----|---------|
| #okta | Autenticação, login |
| #party | Cliente, driver, frota |
| #offer | Cotação, precificação |
| #stipulations | Termos do contrato |
| #contract | Contratos, acordos |
| #delivery | Entrega de veículos |
| #catalog | Catálogo de veículos |
| #general | Sem domínio específico |

---

## 12. Diagnóstico e Troubleshooting

### 12.1 Health Check Rápido

Corre para validar todo o harness:
```bash
python3 ~/Development/teamwill/mobilize/workflow/scripts/harness-health-check.py
```

Output esperado: ~66/67 checks passed (só SonarQube falha se Docker não estiver ativo).

### 12.2 Cenários de Falha Comuns

| Sintoma | Causa Provável | Solução |
|---------|---------------|---------|
| Agente não responde | Timeout (10-15min) | O orchestrator faz retry automático 2x com fallback model. Se persistir → escalado a humano. |
| "MCP not found" | Servidor MCP não está a correr | Verificar com `harness-health-check.py`. Iniciar com `npx gitnexus mcp` (GitNexus) ou `docker compose up` (SonarQube). |
| Plan rejected pelo review-plan | Plano incompleto/incoerente | miles-expert revê com feedback do review-plan (max 2 iterações). Se rejected 2x → humano decide. |
| coherence-checker incoherent | Implementação não segue padrões | Workflow **pára**. Issues são listadas ao humano para decisão (fix manual / continuar). |
| SonarQube quality gate failed | Blocker ou critical issue | Correção automática tentada; se impossível → reportado ao humano. |
| E2E tests failed 3x seguidas | Bug não detectado em análise | Workflow **escala a humano**. Não faz loop infinito. |
| `step-log.py` não escreve | Diretório `logs/` não existe | `mkdir -p ~/Development/teamwill/mobilize/workflow/logs/` |
| Orchestrator não avança | Exit gate não passou | Verificar `step-log.py status <workflow_id>` para ver em que gate está bloqueado. |
| Wiki não sincroniza com Obsidian | sync-obsidian.sh não correu | Executar manualmente: `bash ~/Development/teamwill/mobilize/workflow/scripts/sync-obsidian.sh` |

### 12.3 Ver Estado do Workflow

```bash
# Ver passo actual dum workflow específico
python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py status MMH-1234

# Ver últimas 20 entradas do log
python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py view --tail 20

# Ver só falhas
python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py view --status failure

# Ver estatísticas dos últimos 7 dias
python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py stats --days 7

# Atualizar dashboard Excel com métricas reais
python3 ~/Development/teamwill/mobilize/workflow/scripts/log-metrics.py --update-excel
```

### 12.4 Manutenção Preventiva

| Tarefa | Frequência | Comando |
|--------|-----------|---------|
| Health check completo | Semanal | `python3 scripts/harness-health-check.py` |
| Re-indexar GitNexus | Após mudanças grandes | `npx gitnexus analyze --force` em hyperfront/ e deal-bs/ |
| Verificar integridade da wiki | Mensal | Invocar `@wiki-keeper` com "Executa health check da wiki" |
| Atualizar dashboard de skills | A cada alteração de prompt | Adicionar linha no Excel `ai-skills-dashboard.xlsx` |
| Verificar logs de falhas | Diário (se workflow activo) | `python3 scripts/step-log.py view --status failure` |
| Sincronizar skills globais → workflow | Após alterar qualquer skill | `cp ~/.config/opencode/skills/* ~/workflow/skills/ -r` |

### 12.5 Reset de Workflow

Se um workflow ficar preso ou falhar:

1. Ver estado actual:
   ```bash
   python3 ~/Development/teamwill/mobilize/workflow/scripts/step-log.py status <workflow_id>
   ```
2. Se o workflow está running mas não avança → usar `/stop` no chat
3. Se quiser retomar do início:
   - Remover entry do `_running.json`:
   ```bash
   python3 -c "import json; d=json.load(open('~/Development/teamwill/mobilize/workflow/logs/_running.json')); d.pop('<workflow_id>', None); json.dump(d, open('~/Development/teamwill/mobilize/workflow/logs/_running.json', 'w'))"
   ```
4. Reiniciar o workflow normalmente no chat

---

## 13. Resumo de Preços dos Modelos

| Agente | Modelo | Custo (por 1M tokens) | Retry | Timeout |
|--------|--------|---------------------|-------|----------|
| workflow-orchestrator | opencode/deepseek-v4-flash-free-free | ~$0.40 | - | 10min |
| wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | ~$0.33 | 3 | 5min |
| miles-expert | kilo/deepseek/deepseek-v4-pro | ~$0.70 | 2 | 15min |
| e2e-runner | kilo/stepfun/step-3.5-flash:free | GRÁTIS | 2 | 15min |

---

*Alterações v2.4: Adicionada skill tlc-spec-driven (hybrid SPECIFY+DESIGN). Novo passo 0.6 no workflow-jira-ticket. Novo Gate 1.5 (spec existe, não-bloqueante). 8 skills no total. Novo diretório .specs/ com brownfield mapping (STACK.md, ARCHITECTURE.md, CONVENTIONS.md, STRUCTURE.md, TESTING.md, INTEGRATIONS.md, CONCERNS.md). Exit Criteria do orchestrator atualizado.*
*Alterações v2.3: Adicionado GitNexus (inteligência de código com grafo de conhecimento). Adicionada leitura de emails (.eml) ao wiki-keeper. Modelos atualizados: workflow-orchestrator → deepseek-v4-flash-free, miles-expert → deepseek-v4-pro (mode: all). Adicionadas skills gitnexus-scan e analyze-with-miles-expert.*

*Alterações v2.1: Wiki-keeper pode ler PDFs (texto e imagem via OCR). Requer poppler e tesseract.

*Alterações v2.0: Workflow Orchestrator com 3 modos de operação (auto/plan/build). Modo PLAN para apenas planejamento, modo BUILD para executar a partir de plano existente.

*Alterações v1.9: Nova skill code-quality-checker (v1.0.1) com integração SonarQube automática. Auto-detecção de projeto se chamado independentemente.*

*Alterações v1.8: Verificação automática de princípios de código (DRY, KISS, YAGNI, SOLID, SoC) no step review-implementation. Novo AGENTS.md para deal-bs.*

*Alterações v1.7: Auto-detecção de tipo de projeto (frontend/backend Java/backend Node). Steps dinâmicos para testes e validação.*

*Alterações v1.6: Removidas referências ao projeto Hyperfront - workflow independente de projeto.*

*Alterações v1.5: Geração automática de testes de regressão após validação (step 7.5 generate-regression-test). Template em playwright/tests/regression/template.spec.ts*

*Alterações v1.4: 4 modos de operação (nova/bug/validar/continuar). request-human-approval obrigatório antes de execute-plan. Fluxo de validação de branch.*

*Alterações v1.3: Pasta workflow centralizada com agents/, skills/, e plans/. validator → Step-3.5 Flash (256K context, free)*