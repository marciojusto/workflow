#!/usr/bin/env python3
"""
install-state.py — Helper para gerenciar o state file do instalador e sessões de workflow.
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

STATE_FILE = os.path.expanduser("~/.workflow-installer-state.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get(key: str, default=None):
    return load().get(key, default)


def set(key: str, value):
    state = load()
    state[key] = value
    save(state)


# ─────────────────────────────────────────────────────────────
# Workflow Session Management
# ─────────────────────────────────────────────────────────────

def _ensure_session_schema(state: Dict[str, Any]) -> Dict[str, Any]:
    """Garante que o schema de sessões existe no state."""
    if "sessions" not in state:
        state["sessions"] = {}
    if "current_session_id" not in state:
        state["current_session_id"] = None
    if "workflow_history" not in state:
        state["workflow_history"] = []
    return state


def create_session(workflow_id: str, mode: str = "auto", metadata: Optional[Dict] = None) -> str:
    """Cria uma nova sessão de workflow e retorna o session_id."""
    state = _ensure_session_schema(load())
    
    session_id = str(uuid.uuid4())[:8]
    session = {
        "session_id": session_id,
        "workflow_id": workflow_id,
        "mode": mode,
        "status": "running",  # running | paused | completed | failed | cancelled
        "current_step": "init",
        "current_ac_index": 0,
        "total_acs": 0,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "paused_at": None,
        "completed_at": None,
        "context": metadata or {},
        "checkpoints": [],
        "error": None,
    }
    
    state["sessions"][session_id] = session
    state["current_session_id"] = session_id
    save(state)
    return session_id


def get_session(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Obtém uma sessão pelo ID. Se None, retorna a sessão atual."""
    state = _ensure_session_schema(load())
    
    sid = session_id or state.get("current_session_id")
    if not sid:
        return None
    return state["sessions"].get(sid)


def update_session(session_id: str, **kwargs) -> bool:
    """Atualiza campos de uma sessão."""
    state = _ensure_session_schema(load())
    
    if session_id not in state["sessions"]:
        return False
    
    session = state["sessions"][session_id]
    for key, value in kwargs.items():
        if key in session or key in ["status", "current_step", "current_ac_index", 
                                      "total_acs", "error", "paused_at", "completed_at"]:
            session[key] = value
    
    session["updated_at"] = utc_now()
    save(state)
    return True


def pause_session(session_id: Optional[str] = None, reason: str = "user_request") -> bool:
    """Pausa uma sessão, criando um checkpoint."""
    session = get_session(session_id)
    if not session:
        return False
    
    sid = session["session_id"]
    checkpoint = {
        "timestamp": utc_now(),
        "step": session["current_step"],
        "ac_index": session["current_ac_index"],
        "reason": reason,
    }
    
    state = _ensure_session_schema(load())
    state["sessions"][sid]["checkpoints"].append(checkpoint)
    state["sessions"][sid]["status"] = "paused"
    state["sessions"][sid]["paused_at"] = utc_now()
    save(state)
    return True


def resume_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Resume uma sessão pausada."""
    state = _ensure_session_schema(load())
    
    if session_id not in state["sessions"]:
        return None
    
    session = state["sessions"][session_id]
    if session["status"] != "paused":
        return None
    
    session["status"] = "running"
    session["updated_at"] = utc_now()
    state["current_session_id"] = session_id
    save(state)
    return session


def complete_session(session_id: Optional[str] = None, status: str = "completed") -> bool:
    """Marca uma sessão como completa/falhada/cancelada."""
    session = get_session(session_id)
    if not session:
        return False
    
    sid = session["session_id"]
    
    # Mover para histórico
    state = _ensure_session_schema(load())
    session_copy = state["sessions"][sid].copy()
    session_copy["status"] = status
    session_copy["completed_at"] = utc_now()
    session_copy["updated_at"] = utc_now()
    
    state["workflow_history"].append(session_copy)
    del state["sessions"][sid]
    
    if state["current_session_id"] == sid:
        state["current_session_id"] = None
    
    save(state)
    return True


def list_sessions(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista todas as sessões, opcionalmente filtradas por status."""
    state = _ensure_session_schema(load())
    sessions = list(state["sessions"].values())
    
    if status_filter:
        sessions = [s for s in sessions if s.get("status") == status_filter]
    
    return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)


def get_latest_checkpoint(session_id: str) -> Optional[Dict[str, Any]]:
    """Obtém o checkpoint mais recente de uma sessão."""
    session = get_session(session_id)
    if not session or not session.get("checkpoints"):
        return None
    return session["checkpoints"][-1]


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: install-state.py <command> [args]")
        print("Commands: load | save | get <key> | set <key> <value>")
        print("          session-create <workflow_id> [mode]")
        print("          session-get [session_id]")
        print("          session-update <session_id> <key>=<value> [key=value...]")
        print("          session-pause [session_id] [reason]")
        print("          session-resume <session_id>")
        print("          session-complete [session_id] [status]")
        print("          session-list [status]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "load":
        print(json.dumps(load(), indent=2, ensure_ascii=False))
    elif cmd == "save":
        data = sys.stdin.read()
        save(json.loads(data))
    elif cmd == "get":
        print(get(sys.argv[2] if len(sys.argv) > 2 else ""))
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("Usage: install-state.py set <key> <value>")
            sys.exit(1)
        set(sys.argv[2], sys.argv[3])
    
    # Session commands
    elif cmd == "session-create":
        workflow_id = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        mode = sys.argv[3] if len(sys.argv) > 3 else "auto"
        metadata = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
        sid = create_session(workflow_id, mode, metadata)
        print(json.dumps({"session_id": sid}))
    
    elif cmd == "session-get":
        sid = sys.argv[2] if len(sys.argv) > 2 else None
        session = get_session(sid)
        print(json.dumps(session, indent=2, ensure_ascii=False) if session else "null")
    
    elif cmd == "session-update":
        sid = sys.argv[2]
        kwargs = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                k, v = arg.split("=", 1)
                try:
                    kwargs[k] = json.loads(v)
                except json.JSONDecodeError:
                    kwargs[k] = v
        success = update_session(sid, **kwargs)
        print(json.dumps({"success": success}))
    
    elif cmd == "session-pause":
        sid = sys.argv[2] if len(sys.argv) > 2 else None
        reason = sys.argv[3] if len(sys.argv) > 3 else "user_request"
        success = pause_session(sid, reason)
        print(json.dumps({"success": success}))
    
    elif cmd == "session-resume":
        sid = sys.argv[2]
        session = resume_session(sid)
        print(json.dumps(session, indent=2, ensure_ascii=False) if session else "null")
    
    elif cmd == "session-complete":
        sid = sys.argv[2] if len(sys.argv) > 2 else None
        status = sys.argv[3] if len(sys.argv) > 3 else "completed"
        success = complete_session(sid, status)
        print(json.dumps({"success": success}))
    
    elif cmd == "session-list":
        status_filter = sys.argv[2] if len(sys.argv) > 2 else None
        sessions = list_sessions(status_filter)
        print(json.dumps(sessions, indent=2, ensure_ascii=False))
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
