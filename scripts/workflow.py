#!/usr/bin/env python3
"""
workflow — CLI unificado para gestão de workflows.

Uso:
  python3 workflow.py <comando> [args]

Comandos de Sessão:
  session-create <workflow_id> [mode]      Cria nova sessão
  session-get [session_id]                 Mostra sessão atual ou específica
  session-list [status]                    Lista sessões (running, paused, completed)
  session-pause [session_id] [reason]      Pausa uma sessão
  session-resume <session_id>              Resume sessão pausada
  session-complete [session_id] [status]   Completa sessão

Comandos de Log:
  log-start <wf_id> <agent> <step> [desc] [--session-id SID]
  log-end <wf_id> <agent> <step> <status> [desc] [--session-id SID]
  log-view [wf_id] [--tail N] [--status S] [--agent A]
  log-status <wf_id>
  log-stats [--days N]

Comandos de Validação:
  validate-plan <plan_path> [--current-ac TEXT] [--acs AC1 AC2...]

Comandos de Snapshot/Rollback:
  snapshot-create <session_id> <snapshot_id> <paths...>
  snapshot-list <session_id>
  snapshot-latest <session_id>
  rollback <session_id> [--snapshot-id ID] [--target-dir DIR]

Comandos de Segurança:
  security-scan [--project-root DIR] [--output FILE]
  security-baseline [--project-root DIR] --output FILE
  security-compare [--project-root DIR] --baseline FILE

Comandos de Estado:
  status                                   Mostra estado completo
  checkpoint <session_id> <step> <ac_idx>  Cria checkpoint manual

Exemplos:
  python3 workflow.py session-create MMH-1435 auto
  python3 workflow.py log-start MMH-1435 orchestrator init "Iniciando" --session-id abc123
  python3 workflow.py validate-plan plans/MMH-1435_ac0_plan.md --current-ac "User can login"
  python3 workflow.py snapshot-create abc123 snap1 plans/ .specs/
  python3 workflow.py rollback abc123
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_SCRIPT = os.path.join(SCRIPTS_DIR, "install-state.py")
LOG_SCRIPT = os.path.join(SCRIPTS_DIR, "step-log.py")
VALIDATOR_SCRIPT = os.path.join(SCRIPTS_DIR, "plan-validator.py")
SNAPSHOT_SCRIPT = os.path.join(SCRIPTS_DIR, "snapshot-manager.py")
SECURITY_SCRIPT = os.path.join(SCRIPTS_DIR, "security-scanner.py")


def run_script(script: str, args: list, capture: bool = True) -> str:
    """Run a script and return its output."""
    cmd = [sys.executable, script] + args
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    else:
        subprocess.run(cmd, timeout=30)
        return ""


def print_json(data: str, fallback: str = "{}"):
    """Pretty print JSON."""
    try:
        parsed = json.loads(data) if data else json.loads(fallback)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(data or fallback)


def cmd_session_create(args):
    """Create a new session."""
    if len(args) < 1:
        print("Usage: workflow.py session-create <workflow_id> [mode]")
        sys.exit(1)
    
    workflow_id = args[0]
    mode = args[1] if len(args) > 1 else "auto"
    
    # Pass metadata via stdin
    cmd = [sys.executable, STATE_SCRIPT, "session-create", workflow_id, mode]
    result = subprocess.run(cmd, input="{}", capture_output=True, text=True, timeout=30)
    print_json(result.stdout.strip())


def cmd_session_get(args):
    """Get session details."""
    session_id = args[0] if args else None
    cmd_args = ["session-get"] + ([session_id] if session_id else [])
    output = run_script(STATE_SCRIPT, cmd_args)
    print_json(output)


def cmd_session_list(args):
    """List sessions."""
    status = args[0] if args else None
    cmd_args = ["session-list"] + ([status] if status else [])
    output = run_script(STATE_SCRIPT, cmd_args)
    
    try:
        sessions = json.loads(output) if output else []
        if not sessions:
            print("Nenhuma sessão encontrada.")
            return
        
        print(f"\n{'═' * 80}")
        print(f"  {'SESSION_ID':12} {'WORKFLOW':15} {'STATUS':10} {'STEP':20} {'UPDATED':20}")
        print(f"{'═' * 80}")
        for s in sessions:
            sid = s.get("session_id", "?")[:12]
            wf = s.get("workflow_id", "?")[:15]
            status = s.get("status", "?")
            step = s.get("current_step", "?")[:20]
            updated = s.get("updated_at", "?")[:19]
            
            status_icon = {"running": "🟢", "paused": "🟡", "completed": "✅", "failed": "❌"}.get(status, "⚪")
            print(f"  {sid:12} {wf:15} {status_icon} {status:8} {step:20} {updated:20}")
        print()
    except json.JSONDecodeError:
        print(output)


def cmd_session_pause(args):
    """Pause a session."""
    session_id = args[0] if args else None
    reason = args[1] if len(args) > 1 else "user_request"
    
    if not session_id:
        # Pause current session
        output = run_script(STATE_SCRIPT, ["session-get"])
        try:
            session = json.loads(output)
            session_id = session.get("session_id") if session else None
        except json.JSONDecodeError:
            session_id = None
    
    if not session_id:
        print("❌ Nenhuma sessão ativa para pausar.")
        sys.exit(1)
    
    output = run_script(STATE_SCRIPT, ["session-pause", session_id, reason])
    result = json.loads(output)
    if result.get("success"):
        print(f"⏸️  Sessão {session_id} pausada. Razão: {reason}")
    else:
        print(f"❌ Falha ao pausar sessão {session_id}")


def cmd_session_resume(args):
    """Resume a paused session."""
    if not args:
        print("Usage: workflow.py session-resume <session_id>")
        sys.exit(1)
    
    session_id = args[0]
    output = run_script(STATE_SCRIPT, ["session-resume", session_id])
    
    try:
        session = json.loads(output)
        if session:
            print(f"▶️  Sessão {session_id} resumida.")
            print(f"   Workflow: {session.get('workflow_id')}")
            print(f"   Step atual: {session.get('current_step')}")
            print(f"   AC index: {session.get('current_ac_index')}")
        else:
            print(f"❌ Sessão {session_id} não encontrada ou não está pausada.")
    except json.JSONDecodeError:
        print(output)


def cmd_session_complete(args):
    """Complete a session."""
    session_id = args[0] if args else None
    status = args[1] if len(args) > 1 else "completed"
    
    if not session_id:
        # Complete current session
        output = run_script(STATE_SCRIPT, ["session-get"])
        try:
            session = json.loads(output)
            session_id = session.get("session_id") if session else None
        except json.JSONDecodeError:
            session_id = None
    
    if not session_id:
        print("❌ Nenhuma sessão ativa para completar.")
        sys.exit(1)
    
    output = run_script(STATE_SCRIPT, ["session-complete", session_id, status])
    result = json.loads(output)
    if result.get("success"):
        print(f"✅ Sessão {session_id} marcada como '{status}'.")
    else:
        print(f"❌ Falha ao completar sessão {session_id}")


def cmd_log_start(args):
    """Log step start."""
    # Parse --session-id from args
    session_id = None
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--session-id" and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1
    
    log_args = ["start"] + filtered_args
    if session_id:
        log_args.extend(["--session-id", session_id])
    
    run_script(LOG_SCRIPT, log_args, capture=False)


def cmd_log_end(args):
    """Log step end."""
    session_id = None
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--session-id" and i + 1 < len(args):
            session_id = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1
    
    log_args = ["end"] + filtered_args
    if session_id:
        log_args.extend(["--session-id", session_id])
    
    run_script(LOG_SCRIPT, log_args, capture=False)


def cmd_log_view(args):
    """View logs."""
    run_script(LOG_SCRIPT, ["view"] + args, capture=False)


def cmd_log_status(args):
    """Show workflow status."""
    if not args:
        print("Usage: workflow.py log-status <workflow_id>")
        sys.exit(1)
    run_script(LOG_SCRIPT, ["status", args[0]], capture=False)


def cmd_log_stats(args):
    """Show statistics."""
    run_script(LOG_SCRIPT, ["stats"] + args, capture=False)


def cmd_status(args):
    """Show complete status."""
    print("\n" + "═" * 60)
    print("  📊 Workflow Status")
    print("═" * 60)
    
    # Current session
    output = run_script(STATE_SCRIPT, ["session-get"])
    try:
        session = json.loads(output) if output else None
        if session:
            print(f"\n  🔄 Sessão Ativa: {session.get('session_id')}")
            print(f"     Workflow: {session.get('workflow_id')}")
            print(f"     Status: {session.get('status')}")
            print(f"     Step: {session.get('current_step')}")
            print(f"     AC: {session.get('current_ac_index')}/{session.get('total_acs')}")
            print(f"     Criada: {session.get('created_at', '')[:19]}")
            print(f"     Atualizada: {session.get('updated_at', '')[:19]}")
        else:
            print("\n  ⚪ Nenhuma sessão ativa")
    except json.JSONDecodeError:
        print("\n  ⚪ Nenhuma sessão ativa")
    
    # Recent sessions
    output = run_script(STATE_SCRIPT, ["session-list"])
    try:
        sessions = json.loads(output) if output else []
        if sessions:
            print(f"\n  📋 Sessões Recentes ({len(sessions)}):")
            for s in sessions[:5]:
                status_icon = {"running": "🟢", "paused": "🟡", "completed": "✅", "failed": "❌"}.get(s.get("status"), "⚪")
                print(f"     {status_icon} {s.get('session_id', '?')[:8]} — {s.get('workflow_id', '?')} ({s.get('status')})")
    except json.JSONDecodeError:
        pass
    
    print("\n" + "═" * 60 + "\n")


def cmd_checkpoint(args):
    """Create manual checkpoint."""
    if len(args) < 3:
        print("Usage: workflow.py checkpoint <session_id> <step> <ac_index>")
        sys.exit(1)
    
    session_id, step, ac_index = args[0], args[1], args[2]
    output = run_script(STATE_SCRIPT, ["session-update", session_id, f"current_step={step}", f"current_ac_index={ac_index}"])
    result = json.loads(output)
    if result.get("success"):
        print(f"✅ Checkpoint criado: step={step}, ac_index={ac_index}")
    else:
        print("❌ Falha ao criar checkpoint")


def cmd_validate_plan(args):
    """Validate a plan using advanced validator."""
    if not args:
        print("Usage: workflow.py validate-plan <plan_path> [--current-ac TEXT] [--acs AC1 AC2...]")
        sys.exit(1)
    
    plan_path = args[0]
    extra_args = args[1:]
    
    cmd = [sys.executable, VALIDATOR_SCRIPT, plan_path] + extra_args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    sys.exit(result.returncode)


def cmd_snapshot_create(args):
    """Create a snapshot."""
    if len(args) < 3:
        print("Usage: workflow.py snapshot-create <session_id> <snapshot_id> <paths...>")
        sys.exit(1)
    
    session_id, snapshot_id, paths = args[0], args[1], args[2:]
    
    cmd = [
        sys.executable, SNAPSHOT_SCRIPT, "create",
        "--session-id", session_id,
        "--snapshot-id", snapshot_id,
        "--paths"
    ] + paths
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    print_json(result.stdout.strip())


def cmd_snapshot_list(args):
    """List snapshots for a session."""
    if not args:
        print("Usage: workflow.py snapshot-list <session_id>")
        sys.exit(1)
    
    session_id = args[0]
    output = run_script(SNAPSHOT_SCRIPT, ["list", "--session-id", session_id])
    
    try:
        snapshots = json.loads(output) if output else []
        if not snapshots:
            print("Nenhum snapshot encontrado.")
            return
        
        print(f"\n{'═' * 80}")
        print(f"  {'SNAPSHOT_ID':30} {'CREATED':25} {'STEP':15} {'AUTO':5}")
        print(f"{'═' * 80}")
        for s in snapshots:
            sid = s.get("snapshot_id", "?")[:30]
            created = s.get("created_at", "?")[:19]
            step = s.get("metadata", {}).get("step", "?")[:15]
            auto = "✅" if s.get("metadata", {}).get("auto") else "❌"
            print(f"  {sid:30} {created:25} {step:15} {auto:5}")
        print()
    except json.JSONDecodeError:
        print(output)


def cmd_snapshot_latest(args):
    """Get latest snapshot for a session."""
    if not args:
        print("Usage: workflow.py snapshot-latest <session_id>")
        sys.exit(1)
    
    session_id = args[0]
    output = run_script(SNAPSHOT_SCRIPT, ["latest", "--session-id", session_id])
    print_json(output)


def cmd_security_scan(args):
    """Run security scan."""
    project_root = "."
    output = None
    
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            project_root = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        else:
            i += 1
    
    cmd = [sys.executable, SECURITY_SCRIPT, "scan", "--project-root", project_root]
    if output:
        cmd.extend(["--output", output])
    cmd.append("--format")
    cmd.append("json")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


def cmd_security_baseline(args):
    """Create security baseline."""
    project_root = "."
    output = None
    
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            project_root = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output = args[i + 1]
            i += 2
        else:
            i += 1
    
    if not output:
        print("Error: --output required for baseline")
        sys.exit(1)
    
    cmd = [sys.executable, SECURITY_SCRIPT, "baseline", "--project-root", project_root, "--output", output]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(result.stdout)
    sys.exit(result.returncode)


def cmd_security_compare(args):
    """Compare current scan with baseline."""
    project_root = "."
    baseline = None
    
    i = 0
    while i < len(args):
        if args[i] == "--project-root" and i + 1 < len(args):
            project_root = args[i + 1]
            i += 2
        elif args[i] == "--baseline" and i + 1 < len(args):
            baseline = args[i + 1]
            i += 2
        else:
            i += 1
    
    if not baseline:
        print("Error: --baseline required for compare")
        sys.exit(1)
    
    cmd = [sys.executable, SECURITY_SCRIPT, "compare", "--project-root", project_root, "--baseline", baseline]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(result.stdout)
    sys.exit(result.returncode)


def cmd_rollback(args):
    """Rollback to a snapshot."""
    if not args:
        print("Usage: workflow.py rollback <session_id> [--snapshot-id ID] [--target-dir DIR]")
        sys.exit(1)
    
    session_id = args[0]
    snapshot_id = None
    target_dir = ""
    
    i = 1
    while i < len(args):
        if args[i] == "--snapshot-id" and i + 1 < len(args):
            snapshot_id = args[i + 1]
            i += 2
        elif args[i] == "--target-dir" and i + 1 < len(args):
            target_dir = args[i + 1]
            i += 2
        else:
            i += 1
    
    cmd = [sys.executable, SNAPSHOT_SCRIPT, "rollback", "--session-id", session_id]
    if snapshot_id:
        cmd.extend(["--snapshot-id", snapshot_id])
    if target_dir:
        cmd.extend(["--target-dir", target_dir])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    try:
        data = json.loads(result.stdout.strip())
        if data.get("success"):
            print(f"✅ Rollback concluído para sessão {session_id}")
        else:
            print(f"❌ Rollback falhou para sessão {session_id}")
    except json.JSONDecodeError:
        print(result.stdout)


def usage():
    print(__doc__)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        usage()
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        "session-create": cmd_session_create,
        "session-get": cmd_session_get,
        "session-list": cmd_session_list,
        "session-pause": cmd_session_pause,
        "session-resume": cmd_session_resume,
        "session-complete": cmd_session_complete,
        "log-start": cmd_log_start,
        "log-end": cmd_log_end,
        "log-view": cmd_log_view,
        "log-status": cmd_log_status,
        "log-stats": cmd_log_stats,
        "validate-plan": cmd_validate_plan,
        "snapshot-create": cmd_snapshot_create,
        "snapshot-list": cmd_snapshot_list,
        "snapshot-latest": cmd_snapshot_latest,
        "security-scan": cmd_security_scan,
        "security-baseline": cmd_security_baseline,
        "security-compare": cmd_security_compare,
        "status": cmd_status,
        "checkpoint": cmd_checkpoint,
        "rollback": cmd_rollback,
    }
    
    if cmd not in commands:
        print(f"❌ Comando desconhecido: {cmd}")
        usage()
    
    commands[cmd](args)


if __name__ == "__main__":
    main()
