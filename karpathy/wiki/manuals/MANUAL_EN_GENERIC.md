# Workflow Manual (English)

>  Version: 2.5 | Last Updated: 2026-05-19

## 1. Overview

This workflow is an automated implementation system for Jira tickets that coordinates multiple AI agents to analyze requirements, implement features, and validate results using Playwright E2E tests.

## 2. Workflow Flowchart

```
┌─────────────────┐
│ USER            │
│ Provides Jira   │
│ Ticket ID       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ workflow-       │
│ orchestrator    │
│ Model: deepseek │
│ v4-flash        │
│ Mode: PRIMARY   │
│ Timeout: 10min  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────────┐
│ START │ │ MANUAL        │
│ wiki- │ │ Invocation    │
│ keeper│ │ @wiki-keeper  │
│ Model:│ │ @miles-expert │
│ qwen  │ │ @e2e-runner  │
│ 3.5   │ └───────────────┘
└──┬────┘
   │
   ▼
┌──────────┐
│ miles-   │
│ expert   │
│ Model:   │
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
│ 8 steps          │
│ Timeout: 30min   │
└──────┬───────────┘
       │
       ▼
┌──────────┐
│ e2e-runner│
│ Model:   │
│ Step-3.5 │
│ Flash    │
│ Timeout: │
│ 15min    │
└────┬─────┘
     │
     ▼
┌──────────┐
│ END      │
│ wiki-    │
│ keeper   │
│ Create   │
│ ticket   │
│ note     │
└──────────┘
```

## 3. Agent Descriptions and Functions

### 3.1 workflow-orchestrator

| Attribute | Value |
|-----------|-------|
| **Name** | workflow-orchestrator |
| **Version** | v1.0.3 |
| **Model** | opencode/deepseek-v4-flash-free-free |
| **Fallback Model** | kilo/moonshotai/kimi-k2.7-code |
| **Timeout** | 10 minutes |
| **Mode** | **primary** (user invokes directly) |
| **Primary Function** | Coordinate the complete implementation workflow |

**Responsibilities:**
- Receive user tasks or Jira ticket IDs
- Delegate tasks to appropriate agents in sequence
- Manage error handling and correction cycles
- Request human approval when needed
- Maintain workflow state and traceability

**Error Handling:**
1. If timeout: retry with same model (up to retry limit)
2. If model error: switch to fallback model
3. Log the error in workflow history
4. If all retries exhausted: request human intervention

**Emergency Commands:**
- `/stop` or `/cancel`: Cancel workflow at any time

**When invoked:**
1. User provides a task or Jira ticket ID
2. Orchestrator starts the workflow at step 1 (wiki-keeper)
3. Orchestrator delegates to miles-expert for analysis
4. Orchestrator invokes workflow-jira-ticket for implementation
5. Orchestrator delegates to e2e-runner for testing
6. Orchestrator invokes wiki-keeper at END to create ticket notes
7. If tests fail, orchestrator loops back to miles-expert

### 3.1.1 Orchestrator Operation Modes

The workflow-orchestrator supports three operation modes:

| Mode | Command | Description |
|------|---------|-------------||
| **Auto** | `auto` | Full workflow (planning + execution) |
| **Plan** | `plan` | Planning only, no code execution |
| **Build** | `build` | Execution only, from existing plan |

**Flow by mode:**

```
┌─────────────────────────────────────────────────────────┐
│              WORKFLOW ORCHESTRATOR v1.0.2               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Question: "Which mode? auto/plan/build"                │
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
        │    │ "Planning │  │ Read plan    │
        │    │ complete! │  │ from .json   │
        │    │ Type      │  │              │
        │    │ BUILD"   │  │ request-     │
        │    └────────────┘  │ human-       │
        │                    │ approval     │
        │                    └──────────────┘
        │                           │
        └──────────┬────────────────┘
                   ▼
         ┌─────────────────┐
         │  E2E-RUNNER   │
         │ + WIKI-KEEPER   │
         └─────────────────┘
```

**AUTO Mode (default):**
- Full workflow: wiki-keeper → miles-expert → workflow-jira-ticket (full) → e2e-runner → wiki-keeper

**PLAN Mode:**
- wiki-keeper → miles-expert → workflow-jira-ticket (create-plan + validate-plan only)
- **Stops here** and notifies: "Planning complete. Type BUILD to continue"

**BUILD Mode:**
- Reads plan from `.workflow/history/{ticket_id}.json`
- request-human-approval → workflow-jira-ticket (execute-plan only) → validator → wiki-keeper

**Plan Persistence:**
- Plans are saved to: `.workflow/history/{jira_ticket_id}.json`
- BUILD mode reads this file to continue execution

### 3.2 wiki-keeper

| Attribute | Value |
|-----------|-------|
| **Name** | wiki-keeper |
| **Version** | v1.0.1 |
| **Model** | kilo/qwen/qwen3.5-flash-02-23 |
| **Fallback Model** | kilo/qwen/qwen3.6-flash |
| **Retry** | 3 |
| **Timeout** | 5 minutes |
| **Mode** | subagent |
| **Primary Function** | Knowledge management using the Karpathy Method |

**PDF Reading Capability:**
- wiki-keeper can read PDF files (text or image-based)
- Uses `pdftotext` for selectable text PDFs
- Uses `pdftoppm` + `tesseract` (OCR) for scanned/image PDFs
- Requires tools: `poppler` and `tesseract` (via Homebrew)

**Email (.eml) Reading Capability:**
- wiki-keeper can read .eml email files
- Uses Python's `email` library for full parsing
- Handles multipart emails (text/plain + text/html)
- Decodes headers (From, To, Subject, Date)
- Extracts and cleans body content (removes HTML tags)
- Automatically assigns domain tags: #okta, #party, #offer, #stipulations, #contract, #delivery, #catalog, #general
- Creates notes in `wiki/emails/` directory
- Processes new emails automatically at workflow START

**Responsibilities:**
- Manage personal wiki in Markdown format
- Query existing knowledge in the wiki
- Ingest new documents (PDFs, OpenAPIs, etc.)
- Create ticket notes after implementation
- Perform health checks on wiki structure
- Track processed files in control/log.md

**Operations:**
1. **Query (Search)**: Search existing notes in wiki
2. **Ingestion**: Process new documents and create notes
3. **Health Check**: Find orphaned notes, resolve contradictions
4. **Ticket Note Creation**: Create documentation for implemented tickets

**Wiki Structure:**
```
~/Development/company/project/workflow/karpathy/
├── raw/           # Original immutable documents
├── wiki/         # Generated notes
│   ├── concepts/   # Fundamental concepts
│   ├── references/  # API references, documentation
│   └── projects/    # Ticket implementation notes
├── history/      # Historical records
└── control/      # index.md, log.md
```

### 3.3 miles-expert

| Attribute | Value |
|-----------|-------|
| **Name** | miles-expert |
| **Version** | v1.1.0 |
| **Model** | kilo/deepseek/deepseek-v4-pro |
| **Fallback Model** | kilo/moonshotai/kimi-k2.7-code |
| **Retry** | 2 |
| **Timeout** | 15 minutes |
| **Mode** | subagent |
| **Primary Function** | European automotive domain expert (leasing/financing) |
| **Reasoning** | mode: all (deep reasoning for bug investigation and code analysis) |

**Responsibilities:**
- Deep analysis of Jira tickets (user stories and bugs)
- Identify affected MMP APIs (Miles/Sofico Platform)
- Consult RAG materials (OpenAPI specs, local files)
- Ask clarifying questions before proceeding
- Invoke workflow-jira-ticket for implementation

**Domain Knowledge:**
- 10 MMP APIs: Quotation, Car Quote, Catalog, Dealer POS, Contract, Credit Retail, Customer, Document, Driver, Supplier
- EU vehicle lifecycle regulations
- VAT and tax calculations
- Contract lifecycle: quote → pending → active → terminated

### 3.4 e2e-runner

| Attribute | Value |
|-----------|-------|
| **Name** | e2e-runner |
| **Version** | v1.1.0 |
| **Model** | opencode/deepseek-v4-flash-free |
| **Fallback Model** | openrouter/qwen-3.6-plus |
| **Retry** | 2 |
| **Timeout** | 15 minutes |
| **Mode** | subagent |
| **Primary Function** | E2E testing with Playwright |

**Two Operation Modes:**

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Standalone** | User invokes directly | Asks what to do: Screenshot Analysis or E2E Test |
| **Orchestrated** | Another agent invokes | Runs E2E tests immediately (no questions) |

**Standalone Mode (by user):**
- Asks user to choose: Screenshot Analysis or E2E Test
- Screenshot Analysis: captures/describes system screens in structured Markdown
- E2E Test: validates Acceptance Criteria with Playwright

**Orchestrated Mode (by agent):**
- Executes E2E tests based on structured context (ticket_id, ACs, workflow_id)
- Returns JSON with passed/failed results

**Responsibilities:**
- Execute Playwright E2E tests
- Validate Acceptance Criteria (AC)
- Take screenshots at key validation points
- Provide clear pass/fail feedback
- Include contextId in error output for debugging
- Analyze screenshots and describe in structured Markdown (standalone mode)

**Guidelines:**
- When login expires: let user log in again
- When Data Privacy popup: click "sending by email"
- When postal code required: use 35309
- Proposal phase button enabled after clicking "send secci"

## 4. Agent Delegation Table

| Task | Delegate To | Model | Retry | Timeout |
|------|-------------|-------|-------|----------|
| Knowledge management (start) | @wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | 3 | 5min |
| Knowledge management (end) | @wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | 3 | 5min |
| Deep domain analysis (default) | @miles-expert | kilo/moonshotai/kimi-k2.7-code | 2 | 10min |
| Deep domain analysis (escalation) | @miles-expert | kilo/deepseek/deepseek-v4-pro | 2 | 15min |
| Independent plan review | @review-plan | kilo/z-ai/glm-5.2 | 2 | 10min |
| Architecture coherence validation | @coherence-checker | kilo/moonshotai/kimi-k2.7-code | 2 | 8min |
| Test execution | @e2e-runner | opencode/deepseek-v4-flash-free | 2 | 15min |
| Implementation workflow | @workflow-jira-ticket | (skill) | 2 | 30min |

### Fallback Models
If primary model fails, use these in order:
1. **wiki-keeper**: kilo/qwen/qwen3.6-flash → kilo/qwen/qwen3.5-flash-02-23
2. **miles-expert**: M2.7 default → V4 Pro escalation (on complexity/ambiguity) → V4 Pro fallback (on failure)
3. **e2e-runner**: kilo/moonshotai/kimi-k2.7-code → openrouter/qwen-3.6-plus (self-fallback)

### Miles-Expert Model Selection
- **Default**: Kimi K2.6 (204,800 tokens) for low/medium complexity, single-module analysis
- **Escalation**: DeepSeek V4 Pro (1M tokens) when: high ambiguity, cross-module, large context, high risk
- **Fallback**: If M2.7 fails → escalate to V4 Pro

## 5. Skill Descriptions

### 5.1 workflow-jira-ticket (SKILL)

| Attribute | Value |
|-----------|-------|
| **Name** | workflow-jira-ticket |
| **Type** | Skill (iterative workflow) |
| **Retry** | 2 |
| **Timeout** | 30 minutes |
| **Purpose** | Implement Jira tickets AC by AC |

**4 Operation Modes:**

| Mode | Description |
|------|-------------|
| `nova` | Full implementation for story ticket with ACs |
| `bug` | Bug fix for ticket without ACs |
| `validar` | Validate existing branch (checklist + screenshots) |
| `continuar` | Resume incomplete implementation from history |

**Auto-Detect Project Type:**

The workflow automatically detects the project type:

| Detected Type | File Indicator | Test Framework | Command |
|--------------|----------------|-----------------|----------|
| nuxt-frontend | package.json + playwright.config.ts | Playwright | npx playwright test |
| java-spring-backend | pom.xml + src/test/java | JUnit/Maven | ./mvnw test |
| node-backend | package.json (no playwright) | Jest/Mocha | npm test |

Default paths:
- Frontend: ~/Development/company/project/frontend-app
- Backend (Java): ~/Development/company/project/backend-app
- Backend (Node): detected from project root

**Full Flow:**
0. **mode-selection**: User selects mode (nova/bug/validar/continuar)
0.1 **check-project-guidelines**: Read AGENTS.md for project guidelines
0.2 **check-app-running**: Check if app is running (validate mode only)
0.3 **extract-jira-ticket**: Extract ticket details, ACs, attachments
0.4 **check-all-done**: Check if all ACs completed
0.5 **analyze-with-miles-expert** (MANDATORY - nova/bug/continuar modes only, NOT validar):
   - Deep domain analysis via miles-expert (ALWAYS executed)
   - Input: title, description, ACs, current_ac, project_type
   - Output: domain_analysis, risk_areas, dependencies
   - Used to inform create-plan regardless of complexity

**Validate Mode (1):**
1. **validate-branch**: Run e2e-validator with all ACs → create wiki report → STOP

**Nova/Bug Modes (2-10):**
2. **check-existing-plan**: Verify if plan already exists
3. **create-plan**: Generate implementation plan for current AC
4. **validate-plan**: Validate plan correctness (2 retries)
5. **request-human-approval**: **REQUIRED** - Get approval before executing
   - CRITICAL: NO code changes allowed before approved == true
6. **execute-plan**: Implement the code (ONLY AFTER approved == true)
7. **e2e-validator**: Run E2E tests (calls e2e-runner agent)
7.5 **generate-regression-test**: Auto-generate regression test after successful validation
   - Copies template to `playwright/tests/regression/{ticket_id}_ac{index}.spec.ts`
   - Includes full ticket flow and validator assertions
   - Automatically run in step 8c
8. **review-implementation**: Review code changes (2 retries)
8b. **code-quality-checker**: Check code principles (DRY, KISS, YAGNI, SOLID, SoC) AND run SonarQube automatically
8c. **run-regression-tests**: Execute regression tests
8d. **log-history**: Update implementation history → next AC

### 5.2 e2e-validator (SKILL)

| Attribute | Value |
|-----------|-------|
| **Name** | e2e-validator |
| **Version** | v1.0.1 |
| **Type** | Skill (validation) |
| **Purpose** | Test acceptance criteria using Playwright |

**Inputs:**
- current_ac: The AC to validate
- scope: "current_only" or "all"
- app_url: Target app URL (default: http://localhost:3000)

**Outputs:**
- passed: Boolean
- screenshot_path: Path to screenshot
- error_message: Error description if failed
- contextId: Debug identifier

### 5.3 Code Principles Verification

During **review-implementation** step, the workflow automatically verifies code principles AND runs SonarQube:

| Principle | Frontend (Nuxt/Vue) | Backend (Java/Spring) |
|-----------|---------------------|----------------------|
| **DRY** | Duplicated logic → extract to composables | Duplicated code → extract to services |
| **SoC** | API calls via bsClient (NOT direct fetch) | Proper layer separation (controller → service → repository) |
| **KISS** | Functions < 50 lines | Methods < 30 lines |
| **YAGNI** | No unused imports | No unused imports/methods |
| **SOLID** | Component responsibility | DI, single responsibility per class |
| **Readability First** | Code for humans: clear, readable, no clever tricks | Code for humans: clear, readable, no clever tricks |

**Reference Files:**
- Frontend: `frontend-app/AGENTS.md`
- Backend: `backend-app/AGENTS.md`

**Step: review-implementation → step 2.5 verify-code-principles (code-quality-checker v1.0.1)**
- Automatically verifies principles after code usage check
- If violations found → approved = false, feedback with issues
- If all principles pass → approved = true

### 5.4 Skills That Can Be Invoked Independently

All skills can be called directly via `call: skill.skill-name`, without going through workflow-jira-ticket. This enables modular use for specific tasks.

#### 5.4.1 e2e-validator

| Attribute | Value |
|-----------|-------|
| **Name** | e2e-validator |
| **Version** | v1.0.1 |
| **When to use** | "test this AC", "test E2E", "check UI", "validate implementation" |
| **Auto-detection** | NO - requires explicit inputs |

**Inputs:**
- `current_ac`: Acceptance criteria to test
- `scope`: "current_only" or "all"
- `app_url`: App URL (optional, default: http://localhost:3000)

**Example Call:**
```yaml
- call: skill.e2e-validator
  input:
    - current_ac: "User can see deal status as approved"
    - scope: "current_only"
    - app_url: "http://localhost:3000"
```

#### 5.4.2 code-quality-checker

| Attribute | Value |
|-----------|-------|
| **Name** | code-quality-checker |
| **Version** | v1.0.1 |
| **When to use** | "check code principles", "verify DRY", "check SoC", "code review", "run sonar", "sonar scan" |
| **Auto-detection** | YES - detects project_type if not provided |

**Inputs:**
- `files_modified`: List of changed files
- `project_type`: "nuxt-frontend" | "java-spring-backend" | "node-backend" | "auto" (default: auto)
- `base_path`: Project path (optional)
- `scope`: "full" | "quick" (default: quick)
- `run_sonar`: boolean (default: true)
- `sonar_url`: SonarQube URL (default: http://localhost:9002)
- `sonar_token`: Authentication token (default: pre-generated)

**Example Call:**
```yaml
- call: skill.code-quality-checker
  input:
    - files_modified: ["src/components/DealStatus.vue", "server/api/deals.ts"]
    - project_type: "nuxt-frontend"
    - base_path: "/Users/marcio_oliveira/Development/company/project/frontend-app"
    - run_sonar: true
```

**Independent Call (without project_type):**
```yaml
- call: skill.code-quality-checker
  input:
    - files_modified: ["src/components/DealStatus.vue"]
    - project_type: "auto"  # Auto-detects via pom.xml/package.json
```

#### 5.4.3 log-analyzer-pro

| Attribute | Value |
|-----------|-------|
| **Name** | log-analyzer-pro |
| **Version** | v1.1.0 |
| **When to use** | "analyze logs", "check errors", "debug issue" |
| **Auto-detection** | NO - requires explicit inputs |

**Inputs:**
- `log_path`: Path to log file
- `search_pattern`: Search pattern (optional)
- `error_only`: boolean (optional)

#### 5.4.4 tana-jira-sync

| Attribute | Value |
|-----------|-------|
| **Name** | tana-jira-sync |
| **Version** | v1.1.0 |
| **When to use** | "sync to Tana", "create Tana node", "Jira to Tana" |
| **Auto-detection** | NO - requires explicit inputs |

**Inputs:**
- `jira_ticket_id`: Jira ticket ID
- `workspace`: Tana workspace (optional)

#### 5.4.5 workflow-jira-ticket

| Attribute | Value |
|-----------|-------|
| **Name** | workflow-jira-ticket |
| **Version** | v1.0.5 |
| **When to use** | Full Jira ticket implementation |
| **Auto-detection** | YES - auto-detects project_type |

**Note:** This is the main workflow skill. Can be called independently, but is more commonly invoked by workflow-orchestrator or @miles-expert.

### 5.4.6 tlc-spec-driven

| Attribute | Value |
|-----------|-------|
| **Name** | tlc-spec-driven |
| **Type** | Skill (specification + design) |
| **Source** | Tech Lead's Club (agent-skills.techleads.club) |
| **When to use** | Structured specification for Jira tickets, after ticket data collection |
| **Auto-detection** | YES - auto-sizes depth by complexity |

**Hybrid Integration:**
- **SPECIFY** phase always runs after miles-expert analysis → generates `spec.md` with requirement IDs
- **DESIGN** phase auto-sizes (skipped for straightforward changes, runs only for Large/Complex)
- workflow-jira-ticket uses requirement IDs from spec.md for traceability in create-plan

**Location:** `workflow/skills/tlc-spec-driven/SKILL.md`

**Reference files:** brownfield-mapping.md, specify.md, design.md, implement.md, validate.md, tasks.md, session-handoff.md, quick-mode.md

**Inputs:**
- `jira_ticket_id`: Jira ticket ID
- `mode`: "nova" | "bug" | "validar" | "continuar"

### 5.5 Summary: How to Invoke Skills Independently

| Syntax | Type | Example |
|--------|------|---------|
| `call: skill.name` | Skill (inside workflow) | `call: skill.e2e-validator` |
| `@agent` | Agent (direct invocation) | `@wiki-keeper` |

**Important Note:**
- Skills are invoked with `call: skill.name` **inside a workflow or skill**
- Agents are invoked with `@agent` **directly by the user**
- The `code-quality-checker` skill can auto-detect project type when called independently

### 5.6 When to Use Skill vs Agent

This section explains when it's preferable to invoke a **skill** in isolation versus an **agent** directly.

#### Summary: Skill vs Agent

| Aspect | Skill | Agent |
|--------|-------|-------|
| **Invocation** | `call: skill.name` | `@agent` |
| **Context** | Inside workflow/skill | Direct by user |
| **Abstraction** | Higher (includes guidelines) | Lower (direct prompt) |
| **Complexity** | Multi-step workflows | Simple/direct tasks |
| **Example** | `call: skill.e2e-validator` | `@wiki-keeper` |

#### When to Use SKILL (Recommended)

Use skills when:

| Scenario | Recommended Skill | Reason |
|----------|-------------------|--------|
| Test ACs from a ticket | `skill.e2e-validator` | Already includes guidelines (login, postal code, etc) |
| Verify code principles | `skill.code-quality-checker` | Auto-detects project_type, runs SonarQube |
| Full Jira ticket analysis | `skill.workflow-jira-ticket` | Full flow with human approval |
| Structured specification | `skill.tlc-spec-driven` | Auto-sized SPECIFY + DESIGN with requirement IDs |
| Analyze error logs | `skill.log-analyzer-pro` | Automatic parsing and filtering |
| Sync to Tana | `skill.tana-jira-sync` | Direct Jira + Tana integration |

**Skill Advantages:**
- Already include guidelines and configurations
- Auto-detection of parameters when available
- Optimized workflows for specific tasks
- Less need to specify details in prompt

#### When to Use AGENT (Recommended)

Use agents directly when:

| Scenario | Agent | Reason |
|----------|-------|--------|
| Query wiki knowledge | `@wiki-keeper` | Simple query, no complex workflow |
| Automotive domain questions | `@miles-expert` | Direct analysis, no implementation |
| Administrative tasks | `@workflow-orchestrator` | When manual flow control is needed |

**Agent Advantages:**
- More prompt flexibility
- Direct response without workflow overhead
- Ideal for quick questions or simple tasks

#### Decision Flow

```
I need to do a task...
         │
         ▼
┌─────────────────────────┐
│ Is it a complex task    │
│ with multiple steps?    │
└────────┬────────────────┘
         │
    ┌────┴────┐
    YES      NO
    │         │
    ▼         ▼
┌──────────┐ ┌─────────────────┐
│ USE      │ │ USE AGENT       │
│ SKILL    │ │ DIRECTLY        │
└──────────┘ └─────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ What type of task?                  │
├─────────────┬─────────────┬─────────┤
│ Test AC    │ Code review │ Ticket  │
│ e2e-validator│ code-quality-│workflow-│
│             │ checker     │jira-ticket│
└─────────────┴─────────────┴─────────┘
```

#### Practical Example

**Scenario:** You want to test if an AC was implemented correctly.

| Option | How to Do It | Result |
|--------|--------------|--------|
| **Skill (Recommended)** | `call: skill.e2e-validator` with inputs | Already knows login guidelines, postal code, privacy popup |
| **Agent** | `@e2e-runner` with prompt | Requires specifying guidelines in prompt |

**Conclusion:** For testing ACs, **use the skill** because it already knows the guidelines (login, postal code 35309, etc). For simple wiki queries, **use the agent** directly.

## 6. Can Agents Be Invoked Individually?

**YES** - All agents can be invoked directly without going through workflow-orchestrator.

### 6.1 Direct Invocation Examples

**@wiki-keeper:**
```
Invoke @wiki-keeper to check if we have any knowledge about quotation API
```

**@miles-expert:**
```
Analyze Jira ticket PROJECT-XXXX and identify affected APIs
```

**@e2e-runner:**
```
Validate AC: "User can see deal status as approved after credit approval"
```

### 6.2 Example Prompts for Individual Agents

#### Wiki-keeper Prompts:

| Example | Prompt |
|---------|--------|
| Query existing knowledge | "What do we know about the Quotation API?" |
| Health check | "Run a health check on the wiki" |
| Ingest new document | "Ingest the new OpenAPI spec for miles-contract-v2" |
| Create ticket note | "Create a ticket note for PROJECT-XXXX implementation" |

#### Miles-expert Prompts:

| Example | Prompt |
|---------|--------|
| Analyze ticket | "Analyze Jira ticket PROJECT-XXXX: Create quote workflow" |
| Identify APIs | "Which MMP APIs are affected by vehicle selection feature?" |
| Clarifying questions | "I have questions about VAT handling for multi-country fleets" |

#### e2e-runner Prompts:

| Example | Prompt |
|---------|--------|
| Screenshot analysis | "Analyze the deal page screenshot" or "Capture and describe the dashboard" |
| Test single AC | "Test AC: User can see deal status as approved" |
| Test all ACs | "Run all ACs for ticket PROJECT-XXXX" |
| Debug | "Test AC with contextId DEV-12345-67890" |

## 7. Can Agents Be Invoked Without Prompt?

**PARTIALLY** - Agents require some form of input, but can be invoked with minimal context:

| Agent | Minimum Input | Can Work Without Explicit Prompt? |
|-------|---------------|----------------------------------|
| workflow-orchestrator | Jira Ticket ID or task description | YES - just provide ticket ID |
| wiki-keeper | Action type (query/ingest/health check) | YES - implicit actions |
| miles-expert | Ticket ID or domain question | NEEDS context - cannot work without input |
| e2e-runner | AC to test | NEEDS AC - cannot validate nothing |
| workflow-jira-ticket | Jira Ticket ID | NEEDS ticket - requires structured input |

**Conclusion:** The workflow-orchestrator can work with just a ticket ID. Other agents need more context but the system is designed to provide context automatically through the workflow.

## 8. Error Handling and Recovery

### 8.1 When an Agent Fails:
1. Check if it's a timeout or model error
2. If timeout: retry with same model (up to retry limit)
3. If model error: switch to fallback model
4. Log the error in workflow history
5. If all retries exhausted: request human intervention

### 8.2 Rate Limiting
- Each agent has request limits per minute
- If rate limited: wait 30s before retry
- If persistent: escalate to human

### 8.3 Emergency Stop
To cancel workflow at any time, user can type: `/stop` or `/cancel`
- Current agent will finish gracefully
- Progress will be logged for later resume
- User will be notified of incomplete state

## 9. GitNexus - Code Intelligence

GitNexus provides deep code analysis capabilities for the workflow. It creates a knowledge graph of your codebase, enabling blast radius analysis, dependency tracking, and semantic code search.

### 9.1 Installation and Setup

```bash
# Install CLI globally
npm install -g gitnexus

# Index repositories (run from each repo root)
cd ~/Development/company/project/frontend-app && npx gitnexus analyze
cd ~/Development/company/project/backend-app && npx gitnexus analyze

# Start local server with web UI
gitnexus serve
```

**Web UI:** http://localhost:4747

### 9.2 MCP Configuration

GitNexus is configured via `~/.config/opencode/opencode.json`:

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

### 9.3 Available Tools

| Tool | Purpose |
|------|---------|
| `gitnexus_query` | Semantic search across code |
| `gitnexus_context` | 360° symbol view with refs and process participation |
| `gitnexus_impact` | Blast radius analysis with depth grouping |
| `gitnexus_detect_changes` | Git-diff impact analysis |
| `gitnexus_rename` | Multi-file coordinated rename |
| `gitnexus_cypher` | Raw Cypher graph queries |

### 9.4 Usage in Workflow

GitNexus is **OPTIONAL** and is invoked by miles-expert after step 0.5 (analyze-with-miles-expert):

```
step 0.5: analyze-with-miles-expert (MANDATORY)
          │
          ▼
    miles-expert evaluates:
    "Should I suggest gitnexus-scan?"
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
      (basic only)         → enhanced context
```

### 9.5 Heuristics for Suggestion

**Use GitNexus when:**
- Impact multi-module detected (affects >1 cluster)
- Bug with non-obvious root cause
- Refactoring structural changes
- Low familiarity with code zone
- Need blast radius before planning
- High regression risk

**Don't use when:**
- Small, localized change
- Clearly known area
- Simple, isolated, low-risk ticket

### 9.6 gitnexus-scan Skill

| Attribute | Value |
|-----------|-------|
| **Name** | gitnexus-scan |
| **Type** | Skill (optional) |
| **Location** | `workflow/skills/gitnexus-scan/SKILL.md` |
| **When** | After step 0.5, before create-plan |

**Input:**
- project_type (frontend-app | backend-app)
- jira_ticket_id
- domain_analysis (from miles-expert)
- risk_areas

**Output:**
- impact_analysis (primary/secondary files, blast_radius)
- symbol_analysis (central symbols, call chains)
- recommendations (files to review, tests to verify)

### 9.7 Key Directories

| Directory | Purpose |
|-----------|---------|
| `~/.gitnexus/registry.json` | Global registry of indexed repos |
| `.gitnexus/` (in each repo) | Local index storage |
| `frontend-app/.gitnexus/` | frontend-app index |
| `backend-app/.gitnexus/` | backend-app index |

### 9.8 Important Notes

- **ALL data is LOCAL** - no cloud, no external APIs
- Index must be refreshed after major changes: `gitnexus analyze --force`
- Web UI auto-detects local server at http://localhost:4747

---

## 10. Directory Structure

```
~/Development/company/project/workflow/
├── agents/              # Agent definitions
├── docker/              # Docker configuration for SonarQube scanning
│   ├── docker-compose.yml
│   ├── scan-frontend-app.sh   # SonarQube for frontend projects (Nuxt/Vue/Node)
│   └── scan-backend-app.sh      # SonarQube for Java projects (backend-app)
├── karpathy/            # Wiki system
│   ├── control/          # index.md, log.md
│   ├── history/          # Historical implementation records
│   ├── raw/              # Source documents
│   │   ├── files/        # PDFs, data files (PROJECT_XXXX, PROJECT_YYYY)
│   │   └── openapi/      # 10 MMP API specifications
│   └── wiki/             # Generated notes
│       ├── concepts/     # Concept notes
│       ├── references/   # API references
│       ├── projects/     # Ticket implementation notes
│       └── emails/       # Processed email notes (.eml)
├── plans/                # Implementation plans
├── scripts/              # Utility scripts
│   └── read_excel.py     # Read Excel files from RAG
├── .specs/              # Spec-driven development artifacts (tlc-spec-driven)
│   ├── project/          # PROJECT.md, ROADMAP.md, STATE.md
│   ├── codebase/         # Brownfield mapping (STACK, ARCH, CONVENTIONS, etc.)
│   ├── features/         # Feature specs with requirement IDs
│   └── quick/            # Ad-hoc task docs
├── skills/              # Skill definitions
│   ├── workflow-jira-ticket/      # Main implementation workflow
│   ├── analyze-with-miles-expert/ # Step 0.5 (MANDATORY)
│   ├── tlc-spec-driven/           # Specification + design (hybrid)
│   ├── e2e-validator/            # Test ACs
│   ├── code-quality-checker/     # DRY, SOLID, SonarQube
│   ├── log-analyzer-pro/          # Log analysis
│   ├── tana-jira-sync/            # Jira → Tana
│   └── gitnexus-scan/             # Code analysis (OPTIONAL)
├── tests/               # E2E test outputs
├── MANUAL_EN.md         # English manual
└── MANUAL_PT.md         # Portuguese manual
```

### Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/read_excel.py` | Read Excel files from RAG materials |
| `docker/scan-frontend-app.sh` | Run SonarQube for frontend projects |
| `docker/scan-backend-app.sh` | Run SonarQube for Java projects |
| `docker/docker-compose.yml` | SonarQube container configuration |

## 11. Complete Hierarchy Summary

### Agents (4)

| # | Agent | Model | Version | Mode | Timeout |
|---|-------|-------|--------|------|---------|
| 1 | workflow-orchestrator | deepseek-v4-flash-free | v1.0.3 | primary | 10min |
| 2 | wiki-keeper | deepseek-v4-flash-free | v1.0.3 | subagent | 5min |
| 3 | miles-expert | kimi-k2.7-code / V4 Pro | v1.1.0 | subagent | 10min |
| 4 | review-plan | kilo/z-ai/glm-5.2 | v1.0.0 | subagent | 10min |
| 5 | coherence-checker | minimax-m2.7 | v1.0.0 | subagent | 8min |
| 6 | e2e-runner | deepseek-v4-flash-free | v1.1.0 | subagent | 15min |

### Skills (8)

| # | Skill | Type | When Used |
|---|-------|------|-----------|
| 1 | workflow-jira-ticket | Main workflow | Implementation |
| 2 | analyze-with-miles-expert | Step 0.5 | nova/bug/continuar modes (MANDATORY) |
| 3 | tlc-spec-driven | Spec + Design | After step 0.5, SPECIFY + DESIGN |
| 4 | e2e-validator | Validation | Test ACs |
| 5 | code-quality-checker | Quality | DRY, SOLID, SonarQube |
| 6 | log-analyzer-pro | Debugging | Log analysis |
| 7 | tana-jira-sync | Integration | Jira → Tana |
| 8 | gitnexus-scan | Optional | After step 0.5 (OPTIONAL) |

### workflow-jira-ticket Steps

```
0.  mode-selection
0.1 check-project-guidelines
0.2 check-app-running (validar only)
0.3 extract-jira-ticket
0.4 check-all-done
0.5 analyze-with-miles-expert (MANDATORY - nova/bug/continuar)
    → Optional: gitnexus-scan (if miles-expert suggests + user accepts)
0.6 spec-driven-planning (tlc-spec-driven — hybrid)
    → SPECIFY: .specs/features/{ticket_id}/spec.md
    → DESIGN: .specs/features/{ticket_id}/design.md (Large/Complex only)

1.  validate-branch (validar mode)

2.  check-existing-plan
3.  create-plan (with requirement IDs from spec.md)
4.  validate-plan
5.  request-human-approval (REQUIRED)
6.  execute-plan
7.  e2e-validator
7.5 generate-regression-test (trace-to-playwright.py if test_trace available)
8.  review-implementation
8b. code-quality-checker
8c. run-regression-tests
8d. log-history
```

### Domain Tags for Email

| Tag | Domain |
|-----|--------|
| #okta | Authentication, login |
| #party | Customer, driver, fleet |
| #offer | Quotation, pricing |
| #stipulations | Contract terms |
| #contract | Contracts, agreements |
| #delivery | Vehicle delivery |
| #catalog | Vehicle catalog |
| #general | No specific domain |

---

## 12. Diagnostics and Troubleshooting

### 12.1 Quick Health Check

Run to validate the entire harness:
```bash
python3 ~/Development/company/project/workflow/scripts/harness-health-check.py
```

Expected output: ~66/67 checks passed (only SonarQube fails if Docker not running).

### 12.2 Common Failure Scenarios

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Agent not responding | Timeout (10-15min) | Orchestrator auto-retries 2x with fallback model. If persistent → escalated to human. |
| "MCP not found" | MCP server not running | Check with `harness-health-check.py`. Start with `npx gitnexus mcp` (GitNexus) or `docker compose up` (SonarQube). |
| Plan rejected by review-plan | Incomplete/incoherent plan | miles-expert revises with review-plan feedback (max 2 iterations). If rejected 2x → human decides. |
| coherence-checker incoherent | Implementation doesn't follow patterns | Workflow **stops**. Issues listed to human for decision (manual fix / continue). |
| SonarQube quality gate failed | Blocker or critical issue | Auto-fix attempted; if impossible → reported to human. |
| E2E tests failed 3x in a row | Bug not caught in analysis | Workflow **escalates to human**. No infinite loop. |
| `step-log.py` not writing | `logs/` dir doesn't exist | `mkdir -p ~/Development/company/project/workflow/logs/` |
| Orchestrator not advancing | Exit gate not passed | Check `step-log.py status <workflow_id>` to see which gate is blocked. |
| Wiki not syncing to Obsidian | sync-obsidian.sh didn't run | Run manually: `bash ~/Development/company/project/workflow/scripts/sync-obsidian.sh` |

### 12.3 Check Workflow State

```bash
# View current step of a specific workflow
python3 ~/Development/company/project/workflow/scripts/step-log.py status PROJECT-XXXX

# View last 20 log entries
python3 ~/Development/company/project/workflow/scripts/step-log.py view --tail 20

# View only failures
python3 ~/Development/company/project/workflow/scripts/step-log.py view --status failure

# View stats for last 7 days
python3 ~/Development/company/project/workflow/scripts/step-log.py stats --days 7

# Update Excel dashboard with real metrics
python3 ~/Development/company/project/workflow/scripts/log-metrics.py --update-excel
```

### 12.4 Preventive Maintenance

| Task | Frequency | Command |
|------|-----------|---------|
| Full health check | Weekly | `python3 scripts/harness-health-check.py` |
| Re-index GitNexus | After major changes | `npx gitnexus analyze --force` in frontend-app/ and backend-app/ |
| Check wiki integrity | Monthly | Invoke `@wiki-keeper` with "Run a health check on the wiki" |
| Update skills dashboard | After every prompt change | Add row in `ai-skills-dashboard.xlsx` |
| Check failure logs | Daily (if workflow active) | `python3 scripts/step-log.py view --status failure` |
| Sync global skills → workflow | After any skill change | `cp ~/.config/opencode/skills/* ~/workflow/skills/ -r` |

### 12.5 Workflow Reset

If a workflow gets stuck or fails:

1. Check current state:
   ```bash
   python3 ~/Development/company/project/workflow/scripts/step-log.py status <workflow_id>
   ```
2. If workflow is running but not advancing → use `/stop` in chat
3. To restart from scratch:
   - Remove entry from `_running.json`:
   ```bash
   python3 -c "import json; d=json.load(open('~/Development/company/project/workflow/logs/_running.json')); d.pop('<workflow_id>', None); json.dump(d, open('~/Development/company/project/workflow/logs/_running.json', 'w'))"
   ```
4. Restart the workflow normally in chat

---

## 13. Model Pricing Summary

| Agent | Model | Cost (per 1M tokens) | Retry | Timeout |
|-------|-------|---------------------|-------|----------|
| workflow-orchestrator | opencode/deepseek-v4-flash-free-free | ~$0.40 | - | 10min |
| wiki-keeper | kilo/qwen/qwen3.5-flash-02-23 | ~$0.33 | 3 | 5min |
| miles-expert | kilo/deepseek/deepseek-v4-pro | ~$0.70 | 2 | 15min |
| e2e-runner | opencode/deepseek-v4-flash-free | ~$0.40 | 2 | 15min |

---

*Changes v2.5: e2e-runner v1.1.0 — dual mode (standalone: screenshot analysis + E2E test; orchestrated: E2E only). miles-expert model changed to Kimi K2.6. Removed sonar-scanner Docker service (using native ARM64 binary).*
*Changes v2.3: Added tlc-spec-driven skill (hybrid SPECIFY+DESIGN). New step 0.6 in workflow-jira-ticket. New Gate 1.5 (spec exists, non-blocking). 8 skills total. New .specs/ directory with brownfield mapping (STACK.md, ARCHITECTURE.md, CONVENTIONS.md, STRUCTURE.md, TESTING.md, INTEGRATIONS.md, CONCERNS.md). Updated orchestrator Exit Criteria table.*
*Changes v2.2: Added GitNexus (code intelligence with knowledge graph). Added email (.eml) reading to wiki-keeper. Updated models: workflow-orchestrator → deepseek-v4-flash-free, miles-expert → deepseek-v4-pro (mode: all). Added gitnexus-scan and analyze-with-miles-expert skills.*

*Changes v2.1: Wiki-keeper can read PDFs (text and image via OCR). Requires poppler and tesseract.

*Changes v2.0: Workflow Orchestrator with 3 operation modes (auto/plan/build). PLAN mode for planning only, BUILD mode to execute from existing plan.

*Changes v1.9: New code-quality-checker skill (v1.0.1) with automatic SonarQube integration. Auto-detect project when called independently.*

*Changes v1.8: Automatic code principles verification (DRY, KISS, YAGNI, SOLID, SoC) in review-implementation step. New AGENTS.md for backend-app.*

*Changes v1.7: Auto-detect project type (frontend/backend Java/backend Node). Dynamic steps for testing and validation.*

*Changes v1.6: Removed Frontend project references - workflow is project-agnostic.*

*Changes v1.5: Auto-generate regression tests after validation (step 7.5 generate-regression-test). Template at playwright/tests/regression/template.spec.ts*

*Changes v1.4: 4 operation modes (nova/bug/validar/continuar). request-human-approval required before execute-plan. Branch validation flow.*

*Changes v1.3: Centralized workflow folder with agents/, skills/, and plans/ directories. validator → Step-3.5 Flash (256K context, free)*
### RAG Preprocessing with MarkItDown (v1.1.0)

Both `miles-expert` and `wiki-keeper` use MarkItDown for document preprocessing before RAG ingestion.

**Supported Formats:**
| Format | Extension | Token Savings |
|--------|-----------|---------------|
| Excel | .xlsx, .xls | ~98% (10MB → 200KB) |
| Word | .docx | ~80% |
| PowerPoint | .pptx | ~85% |
| PDF (text) | .pdf | ~70% |
| PDF (image) | .pdf | OCR required |
| HTML/CSS | .html | ~60% |
| CSV/JSON/XML | .csv, .json, .xml | ~50% |

**Benefits:**
- **Cleaner context**: No formatting noise = better LLM understanding
- **Faster processing**: Less tokens = faster responses
- **Lower cost**: Fewer tokens = lower API costs

**Usage:**
```bash
# Convert document to clean Markdown
markitdown /path/to/document.xlsx > /tmp/output.md

# Then process with LLM
cat /tmp/output.md | head -100  # Preview first 100 lines
```

**When to Use:**
- User asks about content in a PDF, Excel, or Word file
- Wiki-keeper provides a raw file path
- Need to extract specific data from documents

## Token Optimization Guide (v2.5)

### Models Pricing

| Model | Input | Output | Cached | Used In |
|-------|-------|--------|--------|---------|
| **deepseek-v4-flash-free** | $0.00 | $0.00 | $0.00 | e2e-runner, wiki-keeper, orchestrator |
| **kimi-k2.7-code** | $0.95 | $4.00 | $0.16 | miles-expert |
| **glm-5.2** | $0.60 | $2.40 | $0.10 | review-plan, coherence-checker |
| **deepseek-v4-pro** | $0.50 | $2.00 | $0.05 | fallback |
| **minimax-m2.7** | $0.30 | $1.20 | $0.05 | fallback |
| **qwen-3.6-plus** | $0.40 | $1.60 | $0.08 | fallback |

### Savings Mechanisms (10 Total)

| # | Mechanism | Savings | Impact |
|---|-----------|---------|--------|
| A | **MarkItDown** | 70-98% per document | HIGH |
| B | **Fallback models** | 50% on retries | MEDIUM |
| C | **Step Logging (NDJSON)** | Less context reprocessing | MEDIUM |
| D | **Page Objects** | ~60% on E2E tests | MEDIUM |
| E | **Prompt versioning** | ~70% per prompt | LOW |
| F | **Selective loading** | 90% per query | HIGH |
| G | **Model tiering** | 80% on simple tasks | HIGH |
| H | **Subagent invocation** | Avoids unnecessary calls | MEDIUM |
| I | **RTK (Run The Kit)** | 30% on CLI commands | MEDIUM |
| J | **GitNexus** | 80-90% on code queries | HIGH |

### Mechanism Details

**A. MarkItDown (Document Preprocessing)**
```bash
# Excel 10MB → Markdown 200KB = 98% token reduction
markitdown ~/raw/files/PROJECT_XXXX/Asset\ Tab.xlsx > /tmp/asset.md

# Word 5MB → Markdown 1MB = 80% reduction
markitdown ~/raw/files/contract.docx > /tmp/contract.md

# PDF 8MB → Markdown 2.4MB = 70% reduction
markitdown ~/raw/files/manual.pdf > /tmp/manual.md
```

**B. Fallback Model Strategy**
```
Flow: Primary Model → Cheaper Fallback → Abort
Example: kimi-k2.7-code ($4.00) → deepseek-v4-pro ($2.00) = 50% savings on retry
```

**C. Step Logging (NDJSON)**
```
Format: NDJSON (not formatted JSON)
Benefit: Reuse context without re-reading files
Example: workflow logs stored in .workflow/logs/step-log.ndjson
```

**D. Page Objects (Playwright)**
```
Before: 1500 tokens per linear test
After: 600 tokens per test with page objects = 60% savings
Benefit: Code reuse, less repetition
```

**E. Prompt Versioning**
```
Example: workflow-jira-ticket v1.0.0 (356 lines) → v1.2.0 (~100 lines)
Benefit: ~70% fewer tokens per prompt
```

**F. Selective Knowledge Loading**
```
Flow: wiki-keeper → load specific endpoints (not all)
Example: 3 endpoints (50KB) vs 25 endpoints (500KB) = 90% savings
```

**G. Model Tiering**
```
Simple tasks: deepseek-v4-flash-free ($0.00)
Medium tasks: glm-5.2 ($0.60/$2.40)
Complex tasks: kimi-k2.7-code ($0.95/$4.00)
```

**H. Subagent Invocation**
```
Flow: Orchestrator decides if miles-expert is needed
Benefit: Avoid unnecessary calls
```

**I. RTK (Run The Kit)**
```bash
# Cache of frequent commands (npm, git, docker)
# Security filters (no dangerous commands)
# Project policies (timeout, automatic retries)
rtk npm install  # vs npm install = cache hit avoids re-download
# Economy: ~30% fewer tokens on CLI commands
```

**J. GitNexus (Code Intelligence)**
```javascript
// Query knowledge graph instead of sending entire files
gitnexus_context("DealService")  // ~200 tokens vs file ~2000 tokens
gitnexus_impact("DealService")   // blast radius analysis without code
gitnexus_query("vehicle search") // semantic search on knowledge graph
gitnexus_cypher()                // structured graph queries
// Economy: ~80-90% fewer tokens on code queries
```

### Total Savings

**75-90% fewer tokens per complete workflow**

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Simple ticket (1 AC) | ~30K tokens | ~8K tokens | 73% |
| Medium ticket (3 ACs) | ~90K tokens | ~22K tokens | 76% |
| Complex ticket (5+ ACs) | ~200K tokens | ~45K tokens | 78% |

**Average cost per ticket: ~4× cheaper**

## Parallel E2E Execution (v2.6)

### Overview

E2E tests can now run in parallel using multiple agents, reducing execution time by 50-67%.

### How It Works

1. **AC Partitioning**: Acceptance Criteria are divided into batches (2-3 ACs each)
2. **Parallel Execution**: Multiple e2e-runner agents execute batches simultaneously
3. **Result Aggregation**: Results are consolidated into a single report

### Batch Distribution

| Total ACs | Batches | Time Savings |
|-----------|---------|--------------|
| 1-2 | 1 | 0% (sequential) |
| 3-4 | 2 | ~50% |
| 5-6 | 3 | ~67% |

### Configuration

No configuration needed - parallel execution is automatic when:
- Ticket has 3+ Acceptance Criteria
- All tests are parallel-safe (unique test data)

### Files

| File | Purpose |
|------|---------|
| `scripts/run-e2e-batch.ts` | Run a batch of tests |
| `scripts/aggregate-e2e-results.ts` | Aggregate batch results |
| `playwright/reports/batches/` | Batch results storage |

### Monitoring

Check parallel execution status:
```bash
# View batch results
python3 workflow/scripts/step-log.py view <workflow_id> --filter e2e-runner

# View aggregated results
cat playwright/reports/batches/aggregated.json
```

### Limitations

- Maximum 3 parallel batches (resource constraint)
- Each batch runs in isolated Playwright instance
- Screenshots saved per-batch in `playwright/reports/batches/<batch-id>/`
