#!/usr/bin/env python3
"""
Step Log — logging centralizado para o workflow harness.

Uso:
  python3 step-log.py <comando> [args]

Comandos:
  start     <workflow_id> <agent> <step> [descrição]
              python3 step-log.py start MMH-1234 miles-expert analyze "Analisar ticket MMH-1234"

  end       <workflow_id> <agent> <step> <status> [output_summary] [error_msg]
              python3 step-log.py end MMH-1234 miles-expert analyze success "Plano criado em plans/..."
              python3 step-log.py end MMH-1234 miles-expert analyze failure "Timeout"

  log       <workflow_id> <agent> <step> <status> <msg>
              python3 step-log.py log MMH-1234 orchestrator dispatch info "A enviar para miles-expert"

  view      [workflow_id] [--tail N] [--status status] [--agent agent]
              python3 step-log.py view MMH-1234
              python3 step-log.py view --tail 20
              python3 step-log.py view --status failure
              python3 step-log.py view --agent miles-expert

  status    <workflow_id>
              python3 step-log.py status MMH-1234

  stats     [--days N]
              python3 step-log.py stats --days 7
"""

import json
import os
import sys
from datetime import datetime, timezone

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

STEP_LOG = os.path.join(LOG_DIR, "step-log.ndjson")
RUNNING_LOG = os.path.join(LOG_DIR, "_running.json")


def _now():
    return datetime.now(timezone.utc).isoformat()


def _read_running():
    if os.path.exists(RUNNING_LOG):
        with open(RUNNING_LOG) as f:
            return json.load(f)
    return {}


def _write_running(data):
    with open(RUNNING_LOG, "w") as f:
        json.dump(data, f, indent=2)


def _read_all():
    entries = []
    if os.path.exists(STEP_LOG):
        with open(STEP_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return entries


def cmd_start(wf_id, agent, step, description=""):
    entry = {
        "timestamp": _now(),
        "workflow_id": wf_id,
        "agent": agent,
        "step": step,
        "event": "start",
        "status": "in_progress",
        "description": description,
        "duration_ms": None,
        "output_summary": None,
        "error": None,
    }
    with open(STEP_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Track running workflows
    running = _read_running()
    if wf_id not in running:
        running[wf_id] = {"started_at": _now(), "steps": [], "current_step": None, "status": "running"}
    running[wf_id]["current_step"] = step
    running[wf_id]["steps"].append({"step": step, "agent": agent, "started_at": _now(), "status": "in_progress"})
    _write_running(running)
    print(json.dumps(entry, ensure_ascii=False))


def cmd_end(wf_id, agent, step, status, output_summary="", error=""):
    started = None

    # Find matching start to compute duration
    entries = _read_all()
    for e in reversed(entries):
        if (e.get("workflow_id") == wf_id and e.get("agent") == agent
                and e.get("step") == step and e.get("event") == "start"):
            started = e["timestamp"]
            break

    duration = None
    if started:
        try:
            start_dt = datetime.fromisoformat(started)
            end_dt = datetime.fromisoformat(_now())
            duration = int((end_dt - start_dt).total_seconds() * 1000)
        except Exception:
            pass

    entry = {
        "timestamp": _now(),
        "workflow_id": wf_id,
        "agent": agent,
        "step": step,
        "event": "end",
        "status": status,
        "description": output_summary or output_summary,
        "duration_ms": duration,
        "output_summary": output_summary,
        "error": error or None,
    }
    with open(STEP_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Update running
    running = _read_running()
    if wf_id in running:
        for s in running[wf_id]["steps"]:
            if s["step"] == step and s["agent"] == agent and s["status"] == "in_progress":
                s["status"] = status
                s["ended_at"] = _now()
                s["duration_ms"] = duration
                break
        running[wf_id]["current_step"] = None
        if status == "failure":
            running[wf_id]["status"] = "failed"
        elif all(s["status"] in ("success", "skipped") for s in running[wf_id]["steps"]):
            running[wf_id]["status"] = "completed"
        _write_running(running)
    print(json.dumps(entry, ensure_ascii=False))


def cmd_log(wf_id, agent, step, status, message=""):
    entry = {
        "timestamp": _now(),
        "workflow_id": wf_id,
        "agent": agent,
        "step": step,
        "event": "log",
        "status": status,
        "description": message,
        "duration_ms": None,
        "output_summary": None,
        "error": None,
    }
    with open(STEP_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(json.dumps(entry, ensure_ascii=False))


DURATION_COLORS = [
    (5000, "\033[32m"),      # <5s green
    (30000, "\033[33m"),     # <30s yellow
    (120000, "\033[38;5;208m"),  # <2min orange
    (float("inf"), "\033[31m"),  # >=2min red
]


def _color_duration(ms):
    if ms is None:
        return "\033[90mN/A\033[0m"
    for limit, color in DURATION_COLORS:
        if ms < limit:
            return f"{color}{ms}ms\033[0m"
    return f"\033[31m{ms}ms\033[0m"


STATUS_COLORS = {
    "success": "\033[32m",
    "failure": "\033[31m",
    "in_progress": "\033[33m",
    "skipped": "\033[90m",
    "running": "\033[33m",
    "completed": "\033[32m",
    "failed": "\033[31m",
}


def _color_status(s):
    c = STATUS_COLORS.get(s, "\033[0m")
    return f"{c}{s}\033[0m"


def cmd_view(wf_id=None, tail=0, status_filter=None, agent_filter=None):
    entries = _read_all()
    if wf_id:
        entries = [e for e in entries if e.get("workflow_id") == wf_id]
    if status_filter:
        entries = [e for e in entries if e.get("status") == status_filter]
    if agent_filter:
        entries = [e for e in entries if e.get("agent") == agent_filter]

    if tail > 0:
        entries = entries[-tail:]

    if not entries:
        print("\033[90mNenhum log encontrado.\033[0m")
        return

    for e in entries:
        ts = e.get("timestamp", "")[11:23]
        wf = e.get("workflow_id", "")
        agent = f"\033[36m{e.get('agent', ''):20}\033[0m"
        step = f"\033[94m{e.get('step', ''):20}\033[0m"
        evt = e.get("event", "")
        evt_icon = {"start": "▶", "end": "■", "log": "●"}.get(evt, " ")
        status = _color_status(e.get("status", ""))
        dur = _color_duration(e.get("duration_ms"))
        desc = e.get("description", "") or ""
        if len(desc) > 60:
            desc = desc[:57] + "..."
        parts = [f"\033[90m{ts}\033[0m", f"{evt_icon}", f"\033[35m{wf:12}\033[0m", agent, step, status, dur]
        if desc:
            parts.append(f"\033[90m{desc}\033[0m")
        print("  ".join(parts))


def cmd_status(wf_id):
    running = _read_running()
    if wf_id not in running:
        # Scan raw log
        entries = _read_all()
        wf_entries = [e for e in entries if e.get("workflow_id") == wf_id]
        if not wf_entries:
            print(f"\033[90mWorkflow '{wf_id}' não encontrado.\033[0m")
            return
        # Reconstruct
        steps_done = set()
        for e in wf_entries:
            if e.get("event") == "end":
                steps_done.add((e.get("step"), e.get("agent")))
        print(f"\033[35m{wf_id}\033[0m — \033[90m{len(steps_done)} steps completed (no running state)\033[0m")
        return

    data = running[wf_id]
    status = _color_status(data["status"])
    print(f"\n{'═' * 60}")
    print(f"  Workflow: \033[35m{wf_id}\033[0m")
    print(f"  Status:   {status}")
    print(f"  Started:  \033[90m{data.get('started_at', '?')[:19]}\033[0m")
    print(f"  Current:  \033[94m{data.get('current_step', '—')}\033[0m")
    print(f"{'═' * 60}")
    for s in data.get("steps", []):
        step_status = _color_status(s["status"])
        dur = _color_duration(s.get("duration_ms"))
        agent = f"\033[36m{s.get('agent', ''):20}\033[0m"
        print(f"  {agent} {s.get('step', ''):20} {step_status} {dur}")
    print()


def cmd_stats(days=7):
    entries = _read_all()
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Filter recent
    recent = []
    for e in entries:
        try:
            dt = datetime.fromisoformat(e.get("timestamp", ""))
            if dt >= cutoff:
                recent.append(e)
        except Exception:
            pass

    if not recent:
        print(f"\033[90mNenhum log nos últimos {days} dias.\033[0m")
        return

    # Count events
    total_steps = len([e for e in recent if e.get("event") == "end"])
    successes = len([e for e in recent if e.get("event") == "end" and e.get("status") == "success"])
    failures = len([e for e in recent if e.get("event") == "end" and e.get("status") == "failure"])
    skipped = len([e for e in recent if e.get("event") == "end" and e.get("status") == "skipped"])

    # Durations
    durations = [e.get("duration_ms") for e in recent if e.get("event") == "end" and e.get("duration_ms")]
    avg_duration = sum(durations) / len(durations) if durations else 0

    # Agents
    agents = set(e.get("agent") for e in recent)
    workflows = set(e.get("workflow_id") for e in recent)

    # Per agent stats
    agent_stats = {}
    for agent in agents:
        agent_ends = [e for e in recent if e.get("agent") == agent and e.get("event") == "end"]
        agent_success = len([e for e in agent_ends if e.get("status") == "success"])
        agent_durs = [e.get("duration_ms") for e in agent_ends if e.get("duration_ms")]
        avg_agent_dur = sum(agent_durs) / len(agent_durs) if agent_durs else 0
        agent_stats[agent] = {
            "total": len(agent_ends),
            "success": agent_success,
            "success_rate": round(agent_success / len(agent_ends) * 100, 1) if agent_ends else 0,
            "avg_duration_ms": round(avg_agent_dur),
        }

    print(f"\n{'═' * 60}")
    print(f"  📊 Estatísticas (últimos {days} dias)")
    print(f"{'═' * 60}")
    print(f"  Workflows:      {len(workflows)}")
    print(f"  Steps total:    {total_steps}")
    print(f"  ✅ Sucesso:     {successes} ({round(successes/total_steps*100, 1) if total_steps else 0}%)")
    print(f"  ❌ Falhas:      {failures} ({round(failures/total_steps*100, 1) if total_steps else 0}%)")
    print(f"  ⏭️  Skips:      {skipped}")
    print(f"  ⏱️  Duração média: {round(avg_duration)}ms ({round(avg_duration/1000, 1)}s)")
    print(f"{'─' * 60}")
    print(f"  Por agente:")
    for agent in sorted(agent_stats.keys()):
        s = agent_stats[agent]
        rate_color = "\033[32m" if s["success_rate"] >= 80 else "\033[33m" if s["success_rate"] >= 50 else "\033[31m"
        print(f"    \033[36m{agent:22}\033[0m {s['total']:3} steps  "
              f"taxa: {rate_color}{s['success_rate']:5.1f}%\033[0m  "
              f"média: {_color_duration(s['avg_duration_ms'])}")
    print()


def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    cmd = sys.argv[1]

    if cmd == "start":
        if len(sys.argv) < 5:
            usage()
        wf_id = sys.argv[2]
        agent = sys.argv[3]
        step = sys.argv[4]
        desc = " ".join(sys.argv[5:]) if len(sys.argv) > 5 else ""
        cmd_start(wf_id, agent, step, desc)

    elif cmd == "end":
        if len(sys.argv) < 6:
            usage()
        wf_id = sys.argv[2]
        agent = sys.argv[3]
        step = sys.argv[4]
        status = sys.argv[5]
        output_summary = " ".join(sys.argv[6:]) if len(sys.argv) > 6 else ""
        cmd_end(wf_id, agent, step, status, output_summary)

    elif cmd == "log":
        if len(sys.argv) < 6:
            usage()
        wf_id = sys.argv[2]
        agent = sys.argv[3]
        step = sys.argv[4]
        status = sys.argv[5]
        msg = " ".join(sys.argv[6:]) if len(sys.argv) > 6 else ""
        cmd_log(wf_id, agent, step, status, msg)

    elif cmd == "view":
        wf_id = None
        tail = 0
        status_filter = None
        agent_filter = None
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--tail":
                i += 1
                tail = int(args[i])
            elif args[i] == "--status":
                i += 1
                status_filter = args[i]
            elif args[i] == "--agent":
                i += 1
                agent_filter = args[i]
            else:
                wf_id = args[i]
            i += 1
        cmd_view(wf_id, tail, status_filter, agent_filter)

    elif cmd == "status":
        if len(sys.argv) < 3:
            usage()
        cmd_status(sys.argv[2])

    elif cmd == "stats":
        days = 7
        if len(sys.argv) > 2:
            if sys.argv[2] == "--days" and len(sys.argv) > 3:
                days = int(sys.argv[3])
        cmd_stats(days)

    else:
        usage()
