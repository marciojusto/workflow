#!/usr/bin/env python3
"""
harness-health-check.py — Valida todos os componentes do workflow harness.

Uso:
  python3 harness-health-check.py                   # Check completo
  python3 harness-health-check.py --quick           # Só checks críticos
  python3 harness-health-check.py --fix             # Tenta corrigir problemas detectados
  python3 harness-health-check.py --preflight       # Preflight rápido (passo 0 do workflow)
  python3 harness-health-check.py --watch           # Monitorização contínua (Ctrl+C para sair)
  python3 harness-health-check.py --watch --interval 30  # A cada 30s
"""

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

# ── Paths ──
WORKFLOW = os.path.expanduser("~/Development/teamwill/mobilize/workflow")
CONFIG_DIR = os.path.expanduser("~/.config/opencode")
AGENTS_DIR = os.path.join(CONFIG_DIR, "agents")
SKILLS_DIR = os.path.join(CONFIG_DIR, "skills")
OPENCODE_JSON = os.path.join(CONFIG_DIR, "opencode.json")
STEP_LOG = os.path.join(WORKFLOW, "logs", "step-log.ndjson")
SCRIPTS_DIR = os.path.join(WORKFLOW, "scripts")
KARPATHY = os.path.join(WORKFLOW, "karpathy")
OBSIDIAN = os.path.expanduser("~/Obsidian/workflow-wiki")
SYNC_SCRIPT = os.path.join(WORKFLOW, "scripts", "sync-obsidian.sh")

REQUIRED_AGENTS = [
    "workflow-orchestrator",
    "wiki-keeper",
    "miles-expert",
    "review-plan",
    "coherence-checker",
    "e2e-runner",
]

REQUIRED_SKILLS = [
    "code-quality-checker",
    "convert-conversation",
    "e2e-validator",
    "extract-jira-ticket",
    "gitnexus-scan",
    "log-analyzer-pro",
    "release-tickets",
    "tana-jira-sync",
    "workflow-jira-ticket",
]

REQUIRED_SCRIPTS = [
    "step-log.py",
    "log-metrics.py",
    "create-excel.py",
    "md-to-html.py",
    "read_excel.py",
    "sync-obsidian.sh",
    "harness-health-check.py",
]

REQUIRED_MCP = [
    "Memory",
    "Filesystem",
    "Playwright",
    "Atlassian",
    "GitNexus",
]

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
WARN = "\033[33m⚠\033[0m"
SKIP = "\033[90m–\033[0m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[90m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"

NEW_PASS = f"\033[32m◄\033[0m"   # green triangle: was failing, now passing
NEW_FAIL = f"\033[31m►\033[0m"   # red triangle: was passing, now failing


class CheckResult:
    """Stores the result of a single check."""
    def __init__(self, name, passed, detail="", section=""):
        self.name = name
        self.passed = passed
        self.detail = detail
        self.section = section


class WatchState:
    """Tracks previous check results for change detection."""
    def __init__(self):
        self.results = {}
        self.iteration = 0
        self.start_time = time.time()

    def update(self, results):
        self.iteration += 1
        changes = []
        for r in results:
            prev = self.results.get(r.name)
            if prev is not None and prev.passed != r.passed:
                changes.append(r)
            self.results[r.name] = r
        return changes

    def uptime(self):
        elapsed = time.time() - self.start_time
        h, rem = divmod(int(elapsed), 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h{m:02d}m{s:02d}s"
        return f"{m:02d}m{s:02d}s"


def check(name, condition, detail="", section=""):
    results.append(CheckResult(name, condition, detail, section))
    return condition


def warn(name, detail, section=""):
    results.append(CheckResult(name, False, detail, section))


def check_mcp_port(name, port, process_name=None, section=""):
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}"],
            capture_output=True, text=True, timeout=5
        )
        running = "LISTEN" in result.stdout
        check(f"MCP {name} ({port})", running, f"não encontrado na porta {port}", section=section)
    except Exception:
        warn(f"MCP {name}", f"não foi possível verificar porta {port}", section=section)


def run_checks():
    """Execute all checks and return list of CheckResult objects."""
    global results
    results = []
    section = ""

    section = "Agentes"
    for agent in REQUIRED_AGENTS:
        path = os.path.join(AGENTS_DIR, f"{agent}.md")
        exists = os.path.isfile(path)
        check(f"agent/{agent}.md", exists, "ficheiro não encontrado", section=section)
        if exists:
            with open(path) as f:
                content = f.read()
            has_model = "model:" in content
            has_retry = "retry:" in content
            check(f"  └─ model definido", has_model, section=section)
            check(f"  └─ retry definido", has_retry, section=section)

    section = "Skills"
    for skill in REQUIRED_SKILLS:
        skill_path = os.path.join(SKILLS_DIR, skill, "SKILL.md") if os.path.isdir(os.path.join(SKILLS_DIR, skill)) else os.path.join(SKILLS_DIR, f"{skill}.md")
        check(f"skill/{skill}", os.path.isfile(skill_path), "ficheiro não encontrado", section=section)

    section = "Scripts"
    for script in REQUIRED_SCRIPTS:
        path = os.path.join(SCRIPTS_DIR, script)
        check(f"scripts/{script}", os.path.isfile(path), "ficheiro não encontrado", section=section)

    section = "MCP Servers"
    if os.path.isfile(OPENCODE_JSON):
        with open(OPENCODE_JSON) as f:
            config = json.load(f)
        mcp_servers = config.get("mcp", {})
        for mcp_name in REQUIRED_MCP:
            exists = mcp_name in mcp_servers
            check(f"MCP {mcp_name} configurado", exists, section=section)
    check_mcp_port("GitNexus", 4747, "gitnexus serve", section=section)

    section = "GitNexus"
    try:
        result = subprocess.run(
            ["npx", "gitnexus", "status"],
            capture_output=True, text=True, timeout=15,
            cwd=os.path.expanduser("~/Development/teamwill/mobilize/hyperfront")
        )
        check("GitNexus CLI", result.returncode == 0, result.stderr[:100], section=section)
    except FileNotFoundError:
        warn("GitNexus CLI", "comando 'npx gitnexus' não encontrado", section=section)
    except Exception as e:
        warn("GitNexus CLI", f"erro: {e}", section=section)

    section = "Estrutura Workflow"
    dirs = [
        (WORKFLOW, "workflow/"),
        (os.path.join(WORKFLOW, "agents"), "workflow/agents/"),
        (os.path.join(WORKFLOW, "skills"), "workflow/skills/"),
        (os.path.join(WORKFLOW, "scripts"), "workflow/scripts/"),
        (os.path.join(WORKFLOW, "logs"), "workflow/logs/"),
        (os.path.join(WORKFLOW, "plans"), "workflow/plans/"),
        (os.path.join(WORKFLOW, "karpathy"), "workflow/karpathy/"),
        (os.path.join(WORKFLOW, "karpathy", "wiki"), "workflow/karpathy/wiki/"),
        (os.path.join(WORKFLOW, "karpathy", "raw"), "workflow/karpathy/raw/"),
        (os.path.join(WORKFLOW, "karpathy", "raw", "files"), "workflow/karpathy/raw/files/"),
        (os.path.join(WORKFLOW, "karpathy", "raw", "openapi"), "workflow/karpathy/raw/openapi/"),
        (os.path.join(WORKFLOW, "karpathy", "control"), "workflow/karpathy/control/"),
    ]
    for dir_path, label in dirs:
        check(f"diretorios/{label}", os.path.isdir(dir_path), section=section)

    section = "Step Log"
    log_dir = os.path.dirname(STEP_LOG)
    check("logs/directory", os.path.isdir(log_dir), section=section)
    if os.path.isfile(STEP_LOG):
        try:
            with open(STEP_LOG) as f:
                lines = [l for l in f if l.strip()]
            check("step-log.ndjournal", True, f"{len(lines)} entradas", section=section)
            if lines:
                last = json.loads(lines[-1])
                age = datetime.now(timezone.utc) - datetime.fromisoformat(last.get("timestamp", "2020-01-01"))
                if age.days > 7:
                    warn("step-log recente", f"última entrada há {age.days} dias", section=section)
        except Exception as e:
            warn("step-log.ndjournal", f"erro ao ler: {e}", section=section)
    else:
        check("step-log.ndjournal", False, "vazio", section=section)

    section = "Wiki Integrity"
    wiki_dirs = {
        "concepts": os.path.join(KARPATHY, "wiki", "concepts"),
        "references": os.path.join(KARPATHY, "wiki", "references"),
        "projects": os.path.join(KARPATHY, "wiki", "projects"),
        "emails": os.path.join(KARPATHY, "wiki", "emails"),
        "conversations": os.path.join(KARPATHY, "wiki", "conversations"),
        "manuals": os.path.join(KARPATHY, "wiki", "manuals"),
    }
    for label, path in wiki_dirs.items():
        if os.path.isdir(path):
            count = len([f for f in os.listdir(path) if f.endswith((".md", ".xlsx"))])
            check(f"wiki/{label}", True, f"{count} ficheiros", section=section)
        else:
            check(f"wiki/{label}", False, section=section)
    for fname in ["index.md", "log.md"]:
        fpath = os.path.join(KARPATHY, "control", fname)
        check(f"control/{fname}", os.path.isfile(fpath), section=section)

    section = "SonarQube"
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:9002"],
            capture_output=True, text=True, timeout=5
        )
        check("SonarQube (porta 9002)", result.stdout == "200",
              f"HTTP {result.stdout}" if result.stdout else "timeout", section=section)
    except Exception:
        warn("SonarQube", "não acessível", section=section)

    section = "Obsidian Sync"
    check("sync-obsidian.sh", os.path.isfile(SYNC_SCRIPT), section=section)
    check("Obsidian vault", os.path.isdir(OBSIDIAN), section=section)
    if os.path.isfile(SYNC_SCRIPT):
        executable = os.access(SYNC_SCRIPT, os.X_OK)
        check("sync-obsidian.sh executável", executable, section=section)

    return results


def print_results(results, changes=None):
    """Pretty-print a list of CheckResult objects, optionally highlighting changes."""
    if changes is None:
        changes = []

    change_names = {c.name for c in changes}
    change_map = {c.name: c for c in changes}

    sections = {}
    for r in results:
        sections.setdefault(r.section, []).append(r)

    for section_name, section_results in sections.items():
        print(f"  {BOLD}{section_name}{RESET}")
        for r in section_results:
            if r.passed:
                print(f"  {PASS} {r.name}")
            else:
                detail = f"  {DIM}{r.detail}{RESET}" if r.detail else ""
                print(f"  {FAIL} {r.name}  {detail}" if r.detail else f"  {FAIL} {r.name}")
        print()


def print_summary(results, changes=None, state=None):
    """Print final summary block."""
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    failed = [r for r in results if not r.passed]

    if changes:
        newly_passed = [c for c in changes if c.passed]
        newly_failed = [c for c in changes if not c.passed]
        change_summary = ""
        if newly_passed:
            change_summary += f" {GREEN}+{len(newly_passed)}{RESET}"
        if newly_failed:
            change_summary += f" {RED}-{len(newly_failed)}{RESET}"
    else:
        change_summary = ""

    print(f"{'═' * 56}")
    status = f"{PASS} {passed}/{total} passed"
    if passed == total:
        print(f"  Resultado: {status}{change_summary}")
    else:
        print(f"  Resultado: {status}{change_summary}")
        print(f"  {FAIL} Falhas ({len(failed)}):")
        for f in failed:
            print(f"    • {f.name}{' — ' + f.detail if f.detail else ''}")
    if state:
        print(f"  {DIM}uptime: {state.uptime()}  iteração #{state.iteration}{RESET}")
    print(f"{'═' * 56}")


def run_preflight_checks():
    """Fast preflight: only validates essentials before a workflow run.
    Skips: GitNexus port, GitNexus CLI, SonarQube, wiki file counts, step-log content.
    """
    global results
    results = []
    ok = True

    # Agents (CRITICAL)
    missing_agents = []
    for agent in REQUIRED_AGENTS:
        if not os.path.isfile(os.path.join(AGENTS_DIR, f"{agent}.md")):
            missing_agents.append(agent)
    if missing_agents:
        print(f"  {FAIL} agentes em falta: {', '.join(missing_agents)}")
        ok = False
    else:
        print(f"  {PASS} 6 agentes encontrados")

    # Skills (CRITICAL)
    missing_skills = []
    for skill in REQUIRED_SKILLS:
        skill_path = os.path.join(SKILLS_DIR, skill, "SKILL.md") if os.path.isdir(os.path.join(SKILLS_DIR, skill)) else os.path.join(SKILLS_DIR, f"{skill}.md")
        if not os.path.isfile(skill_path):
            missing_skills.append(skill)
    if missing_skills:
        print(f"  {FAIL} skills em falta: {', '.join(missing_skills)}")
        ok = False
    else:
        print(f"  {PASS} 9 skills encontradas")

    # Scripts (CRITICAL)
    missing_scripts = []
    for script in REQUIRED_SCRIPTS:
        if not os.path.isfile(os.path.join(SCRIPTS_DIR, script)):
            missing_scripts.append(script)
    if missing_scripts:
        print(f"  {FAIL} scripts em falta: {', '.join(missing_scripts)}")
        ok = False
    else:
        print(f"  {PASS} 7 scripts encontrados")

    # MCP Config (CRITICAL)
    if os.path.isfile(OPENCODE_JSON):
        with open(OPENCODE_JSON) as f:
            config = json.load(f)
        mcp_servers = config.get("mcp", {})
        missing_mcp = [m for m in REQUIRED_MCP if m not in mcp_servers]
        if missing_mcp:
            print(f"  {FAIL} MCP não configurados: {', '.join(missing_mcp)}")
            ok = False
        else:
            print(f"  {PASS} 5 MCP configurados")
    else:
        print(f"  {FAIL} opencode.json não encontrado")
        ok = False

    # Workflow directories (CRITICAL)
    required_dirs = [
        WORKFLOW,
        os.path.join(WORKFLOW, "logs"),
        os.path.join(WORKFLOW, "plans"),
        os.path.join(WORKFLOW, "karpathy"),
        os.path.join(WORKFLOW, "karpathy", "wiki"),
    ]
    missing_dirs = [d for d in required_dirs if not os.path.isdir(d)]
    if missing_dirs:
        print(f"  {FAIL} diretórios em falta: {', '.join(missing_dirs)}")
        ok = False
    else:
        print(f"  {PASS} diretórios OK")

    # Obsidian (NON-CRITICAL — warning only)
    obs_ok = True
    if not os.path.isfile(SYNC_SCRIPT):
        print(f"  {WARN} sync-obsidian.sh não encontrado (wiki não será sincronizada)")
        obs_ok = False
    if not os.path.isdir(OBSIDIAN):
        print(f"  {WARN} Obsidian vault não encontrado em {OBSIDIAN}")
        obs_ok = False
    if os.path.isfile(SYNC_SCRIPT) and not os.access(SYNC_SCRIPT, os.X_OK):
        print(f"  {WARN} sync-obsidian.sh sem permissão de execução")
        obs_ok = False
    if obs_ok:
        print(f"  {PASS} Obsidian sync OK")

    return ok


def print_preflight_result(ok):
    """Print preflight result block. Machine-parseable for the orchestrator."""
    if ok:
        print(f"\n{PASS} PREFLIGHT PASSED — ambiente pronto para workflow")
    else:
        print(f"\n{FAIL} PREFLIGHT FAILED — corrija as falhas antes de iniciar")
    print()


def main_preflight():
    """Preflight mode: called by orchestrator at step 0."""
    print(f"  {BOLD}🔍 Preflight: Verificando ambiente...{RESET}")
    ok = run_preflight_checks()
    print_preflight_result(ok)
    return ok


def main_single():
    """Single-run mode."""
    r = run_checks()
    print_results(r)
    print_summary(r)
    return sum(1 for rr in r if rr.passed) == len(r)


def main_watch(interval, max_iterations=None):
    """Watch mode: continuously re-run and show changes."""
    state = WatchState()

    def handle_sigint(sig, frame):
        print(f"\n{DIM}👋 Watch terminated. Ran {state.iteration} checks over {state.uptime()}.{RESET}")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    print(f"\n{'═' * 56}")
    print(f"  👁  Watch Mode — Ctrl+C para sair")
    print(f"  {DIM}intervalo: {interval}s{RESET}")
    print(f"{'═' * 56}\n")

    while True:
        r = run_checks()
        changes = state.update(r)

        now = datetime.now(timezone.utc).strftime("%H:%M:%S")
        passed = sum(1 for rr in r if rr.passed)
        total = len(r)

        status_color = GREEN if passed == total else RED
        print(f"{BOLD}─── #{state.iteration} @ {now} — status: {status_color}{passed}/{total}{RESET}{BOLD} │ uptime: {state.uptime()}{RESET} ───")

        if changes:
            print(f"  {YELLOW}═══ Changes detected ({len(changes)}) ═══{RESET}")
            for c in changes:
                icon = NEW_PASS if c.passed else NEW_FAIL
                direction = f"{GREEN}RECOVERED{RESET}" if c.passed else f"{RED}FAILING{RESET}"
                print(f"  {icon} {c.name} → {direction} {DIM}{c.detail}{RESET}")
            print()
        else:
            print(f"  {DIM}(no changes since last check){RESET}\n")

        print(f"  {DIM}result: {passed}/{total} passed, {total - passed} failed{RESET}")
        print(f"{'─' * 56}\n")

        if max_iterations and state.iteration >= max_iterations:
            break

        for _ in range(interval):
            time.sleep(1)

    print(f"  {DIM}👋 Done — {state.iteration} iterations over {state.uptime()}{RESET}")


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    do_fix = "--fix" in sys.argv
    watch = "--watch" in sys.argv or "-w" in sys.argv
    preflight = "--preflight" in sys.argv

    interval = 60
    if "--interval" in sys.argv:
        idx = sys.argv.index("--interval")
        if idx + 1 < len(sys.argv):
            interval = int(sys.argv[idx + 1])
    if quick:
        interval = 30

    max_iterations = None
    if "--iterations" in sys.argv:
        idx = sys.argv.index("--iterations")
        if idx + 1 < len(sys.argv):
            max_iterations = int(sys.argv[idx + 1])

    if preflight:
        success = main_preflight()
    elif watch:
        main_watch(interval, max_iterations)
    else:
        success = main_single()

    if not success:
        sys.exit(1)
