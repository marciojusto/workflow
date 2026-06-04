---
name: code-quality-checker
version: v1.0.1
description: Verify code follows DRY, KISS, YAGNI, SOLID, SoC principles AND run SonarQube scan. Uses explore agent with qwen3.5-flash model.
---

# Code Quality Checker

## Config
on_error: report_and_continue

## Inputs
- files_modified: list of files changed (required)
- project_type: "nuxt-frontend" | "java-spring-backend" | "node-backend" | "auto" (optional, defaults to "auto")
- base_path: path to project root (optional, defaults to current directory)
- scope: "full" | "quick" (optional, defaults to "quick")
- run_sonar: boolean (optional, defaults to true)
- sonar_url: string (optional, defaults to http://localhost:9002)
- sonar_token: string (optional, defaults to squ_278bc6fee0a5864b9ce811532790b8eb722668bd)

## Output
- all_passed: boolean
- code_principles_passed: boolean
- dry_violations: array of objects
- kiss_violations: array of objects
- yagni_violations: array of objects
- solid_violations: array of objects
- soc_violations: array of objects
- code_principles_summary: string
- sonar_result:
  - executed: boolean
  - gate_passed: boolean
  - quality_gate_status: "OK" | "ERROR"
  - metrics:
    - bugs: number
    - code_smells: number
    - coverage: number
    - duplications: number
    - lines_of_code: number
    - maintainability: string (A-F)
    - reliability: string (A-F)
    - security: string (A-F)
  - new_issues: number
  - url: string
  - scanned_at: string
  - error: string (if scan failed)
- summary: string
- contextId: string (for failed checks)

## When use
- Use when asked to "check code principles", "verify DRY", "check SoC", "code review", "validate code quality"
- Use for "run sonar", "sonar scan", "code analysis"
- Called automatically in review-implementation step 2.5
- Can be called independently for specific files

## Project Type Auto-Detection

If project_type is not provided or is "auto", detect by checking files:

```
if not provided or project_type == "auto":
  check_path = base_path or current_directory
  
  if check_path contains "pom.xml":
    → project_type = "java-spring-backend"
  else if check_path contains "package.json" AND contains "playwright.config.ts":
    → project_type = "nuxt-frontend"
  else if check_path contains "package.json":
    → project_type = "node-backend"
  else:
    → error: "Cannot auto-detect project type. Please specify project_type."
```

## Guidelines

### DRY - Don't Repeat Yourself
- Detect duplicated code patterns
- Find repeated logic that should be extracted to utilities
- For Nuxt: check for repeated composables, duplicated API calls
- For Java: check for duplicated methods, repeated utility classes

### KISS - Keep It Simple, Stupid
- Check method/function complexity
- Flag functions with too many responsibilities
- Check for unnecessary nested conditions

### YAGNI - You Aren't Gonna Need It
- Detect unused imports
- Find dead code
- Check for over-engineering

### SOLID Principles
- **S**ingle Responsibility: Each class/function does one thing
- **O**pen/Closed: Check for proper abstraction
- **L**iskov Substitution: Verify interface usage
- **I**nterface Segregation: Check for large interfaces
- **D**ependency Inversion: Verify proper dependencies

### SoC - Separation of Concerns
- For Nuxt frontend: API calls must use bsClient pattern (never direct fetch in components)
- For Java backend: Check layer separation (controller/service/repository)
- Verify business logic separated from UI/code

## Project-Specific Rules

### nuxt-frontend
- API calls MUST use bsClient from server/services/bsClient.ts
- NEVER create new fetch functions in Vue components
- Use Pinia stores for state management
- All text from i18n files

### java-spring-backend
- Check layer separation: controller → service → repository
- Use proper dependency injection
- Check for @Transactional boundaries

### node-backend
- Follow same SoC as frontend - API calls in routes/services
- Check for proper middleware separation

## SonarQube Integration

### Auto-detect sonar command based on project_type:

| project_type | Command | Working Directory |
|--------------|---------|-------------------|
| nuxt-frontend | `npx sonar-scanner -Dsonar.projectKey={projectKey}` | base_path |
| java-spring-backend | `./mvnw sonar:sonar -Dsonar.projectKey={projectKey}` | base_path |
| node-backend | `npx sonar-scanner -Dsonar.projectKey={projectKey}` | base_path |

### Project Key Auto-detection:

```
if project_type == "nuxt-frontend":
  project_key = "hyperfront" (or from package.json name)
if project_type == "java-spring-backend":
  project_key = "deal-bs" (or from pom.xml artifactId)
if project_type == "node-backend":
  project_key = from package.json name
```

### Sonar URL:
- Use provided sonar_url, or
- Default: http://localhost:9002

### Sonar Token:
- Use provided sonar_token, or
- Default: squ_278bc6fee0a5864b9ce811532790b8eb722668bd (pre-generated for admin)
- Token can be generated via: `curl -s -u admin:admin -X POST "http://localhost:9002/api/user_tokens/generate?name=scanner"`

## Steps

1. detect-project-type
   - input: project_type, base_path
   - logic:
     - if project_type and project_type != "auto":
         → use provided value
     - else:
         → auto-detect from files (pom.xml, package.json, playwright.config.ts)
     - determine sonar command based on detected type
     - determine project_key from package.json or pom.xml

2. invoke-code-quality-agent
   - call: task
   - input:
     command: Analyze code quality and principles
     subagent_type: explore
     prompt: |
       Analyze the following files for code quality principles:
       
       - files_modified: {files_modified}
       - project_type: {project_type}
       - base_path: {base_path}
       - scope: {scope}
       
       Check for violations of:
       1. DRY (Don't Repeat Yourself)
       2. KISS (Keep It Simple)
       3. YAGNI (You Aren't Gonna Need It)
       4. SOLID (Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion)
       5. SoC (Separation of Concerns)
       
       For nuxt-frontend specifically:
       - Verify API calls use bsClient pattern (server/services/bsClient.ts)
       - Check NO direct fetch() in Vue components
       - Verify Pinia store usage for state
       
       For java-spring-backend:
       - Check controller/service/repository layer separation
       - Verify @Transactional usage
       - Check proper DI with @Autowired or constructor
       
       For node-backend:
       - Verify API calls in routes/services, not inline
       - Check middleware separation
       
       Return results in this format:
       ```json
       {
         "all_passed": true,
         "dry_violations": [],
         "kiss_violations": [],
         "yagni_violations": [],
         "solid_violations": [],
         "soc_violations": [],
         "summary": "All code principles verified successfully. No violations found."
       }
       ```
       
       If violations found:
       ```json
       {
         "all_passed": false,
         "dry_violations": [
           {"file": "src/components/Foo.vue", "line": 45, "issue": "Duplicate code found in Bar.vue line 78"}
         ],
         "kiss_violations": [],
         "yagni_violations": [],
         "solid_violations": [],
         "soc_violations": [
           {"file": "src/components/Baz.vue", "line": 12, "issue": "Direct fetch() call found - must use bsClient"}
         ],
         "summary": "2 violations found: 1 DRY, 1 SoC"
       }
       ```

3. run-sonar-scan
   - if run_sonar == false:
     → skip this step, sonar_result.executed = false
   - input:
     - project_type (from step 1)
     - base_path
     - project_key (from step 1)
     - sonar_url
     - sonar_token (defaults to pre-generated token)
   - logic:
     - if project_type == "nuxt-frontend" or "node-backend":
         - command: cd {base_path} && npx sonar-scanner \
           -Dsonar.projectKey={project_key} \
           -Dsonar.token={sonar_token} \
           -Dsonar.login={sonar_token} \
           -Dsonar.sources=./ \
           -Dsonar.exclusions=node_modules,dist,.nuxt \
           -Dsonar.host.url={sonar_url}
     - if project_type == "java-spring-backend":
         - command: cd {base_path} && ./mvnw sonar:sonar \
           -Dsonar.projectKey={project_key} \
           -Dsonar.token={sonar_token} \
           -Dsonar.login={sonar_token} \
           -Dsonar.java.source=17 \
           -Dsonar.host.url={sonar_url}
   - on_error: report_and_continue
   - timeout: 300000ms (5 minutes)
   - parse output to extract metrics

4. extract-result
   - input:
     - code_principles_result from step 2
     - sonar_result from step 3
   - logic:
     - code_principles_passed = code_principles_result.all_passed
     - sonar_gate_passed = sonar_result.quality_gate_status == "OK"
     - all_passed = code_principles_passed AND (not sonar_result.executed OR sonar_gate_passed)
     
     - if sonar_result.executed and not sonar_gate_passed:
         - warning: "SonarQube quality gate failed, but continuing as configured"
     
     - summary = code_principles_result.summary + " | SonarQube: " + (sonar_result.quality_gate_status or "not executed")
   - output: all_passed, code_principles_passed, dry_violations, kiss_violations, yagni_violations, solid_violations, soc_violations, code_principles_summary, sonar_result, summary, contextId