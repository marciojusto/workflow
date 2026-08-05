#!/usr/bin/env python3
"""
snapshot-manager.py — Sistema de snapshots para rollback automático.

Cria snapshots do estado antes de passos críticos e permite rollback.
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

SNAPSHOT_DIR = os.path.join(os.path.expanduser("~"), ".workflow", "snapshots")
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_snapshot_path(session_id: str, snapshot_id: str) -> str:
    """Get path for a specific snapshot."""
    return os.path.join(SNAPSHOT_DIR, session_id, f"{snapshot_id}.tar.gz")


def get_snapshot_metadata_path(session_id: str, snapshot_id: str) -> str:
    """Get metadata path for a specific snapshot."""
    return os.path.join(SNAPSHOT_DIR, session_id, f"{snapshot_id}.json")


def ensure_session_dir(session_id: str) -> str:
    """Ensure session snapshot directory exists."""
    session_dir = os.path.join(SNAPSHOT_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir


def create_snapshot(
    session_id: str,
    snapshot_id: str,
    paths: List[str],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a snapshot of specified paths."""
    ensure_session_dir(session_id)
    
    snapshot_path = get_snapshot_path(session_id, snapshot_id)
    metadata_path = get_snapshot_metadata_path(session_id, snapshot_id)
    
    # Create tarball
    with tarfile.open(snapshot_path, "w:gz") as tar:
        for path in paths:
            if os.path.exists(path):
                arcname = os.path.basename(path)
                if os.path.isdir(path):
                    tar.add(path, arcname=arcname)
                else:
                    tar.add(path, arcname=arcname)
    
    # Save metadata
    snapshot_meta = {
        "snapshot_id": snapshot_id,
        "session_id": session_id,
        "created_at": utc_now(),
        "paths": paths,
        "metadata": metadata or {},
    }
    
    with open(metadata_path, "w") as f:
        json.dump(snapshot_meta, f, indent=2, ensure_ascii=False)
    
    return snapshot_meta


def restore_snapshot(session_id: str, snapshot_id: str, target_dir: str = "") -> bool:
    """Restore a snapshot to its original location or target directory."""
    snapshot_path = get_snapshot_path(session_id, snapshot_id)
    
    if not os.path.exists(snapshot_path):
        return False
    
    extract_to = target_dir or tempfile.mkdtemp(prefix="workflow_restore_")
    
    with tarfile.open(snapshot_path, "r:gz") as tar:
        tar.extractall(path=extract_to)
    
    return True


def list_snapshots(session_id: str) -> List[Dict[str, Any]]:
    """List all snapshots for a session."""
    session_dir = os.path.join(SNAPSHOT_DIR, session_id)
    if not os.path.exists(session_dir):
        return []
    
    snapshots = []
    for filename in os.listdir(session_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(session_dir, filename)
            with open(filepath, "r") as f:
                snapshots.append(json.load(f))
    
    return sorted(snapshots, key=lambda x: x.get("created_at", ""), reverse=True)


def get_latest_snapshot(session_id: str) -> Optional[Dict[str, Any]]:
    """Get the most recent snapshot for a session."""
    snapshots = list_snapshots(session_id)
    return snapshots[0] if snapshots else None


def delete_snapshot(session_id: str, snapshot_id: str) -> bool:
    """Delete a specific snapshot."""
    snapshot_path = get_snapshot_path(session_id, snapshot_id)
    metadata_path = get_snapshot_metadata_path(session_id, snapshot_id)
    
    deleted = False
    if os.path.exists(snapshot_path):
        os.remove(snapshot_path)
        deleted = True
    if os.path.exists(metadata_path):
        os.remove(metadata_path)
        deleted = True
    
    return deleted


def cleanup_old_snapshots(session_id: str, keep_count: int = 5) -> int:
    """Delete old snapshots, keeping only the most recent N."""
    snapshots = list_snapshots(session_id)
    if len(snapshots) <= keep_count:
        return 0
    
    to_delete = snapshots[keep_count:]
    deleted = 0
    for snap in to_delete:
        if delete_snapshot(session_id, snap["snapshot_id"]):
            deleted += 1
    
    return deleted


def auto_snapshot_before_step(
    session_id: str,
    step_name: str,
    paths_to_snapshot: List[str],
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Automatically create a snapshot before a critical step."""
    snapshot_id = f"auto_{step_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    # Filter to existing paths only
    existing_paths = [p for p in paths_to_snapshot if os.path.exists(p)]
    
    if not existing_paths:
        return None
    
    meta = metadata or {}
    meta["step"] = step_name
    meta["auto"] = True
    
    create_snapshot(session_id, snapshot_id, existing_paths, meta)
    
    # Cleanup old snapshots
    cleanup_old_snapshots(session_id, keep_count=10)
    
    return snapshot_id


def rollback_to_snapshot(
    session_id: str,
    snapshot_id: Optional[str] = None,
    target_dir: str = ""
) -> bool:
    """Rollback to a specific snapshot or the latest one."""
    if snapshot_id is None:
        latest = get_latest_snapshot(session_id)
        if not latest:
            return False
        snapshot_id = latest["snapshot_id"]
    
    return restore_snapshot(session_id, snapshot_id, target_dir)


def main():
    parser = argparse.ArgumentParser(description="Snapshot Manager")
    parser.add_argument("command", choices=[
        "create", "restore", "list", "latest", "delete", "cleanup", "rollback", "auto"
    ])
    parser.add_argument("--session-id", required=True, help="Session ID")
    parser.add_argument("--snapshot-id", help="Snapshot ID")
    parser.add_argument("--paths", nargs="*", help="Paths to snapshot")
    parser.add_argument("--metadata", help="JSON metadata")
    parser.add_argument("--step", help="Step name for auto snapshot")
    parser.add_argument("--keep", type=int, default=5, help="Number of snapshots to keep")
    parser.add_argument("--target-dir", default="", help="Target directory for restore")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    
    args = parser.parse_args()
    
    result = None
    
    if args.command == "create":
        if not args.snapshot_id or not args.paths:
            print("Error: --snapshot-id and --paths required for create", file=sys.stderr)
            sys.exit(1)
        metadata = json.loads(args.metadata) if args.metadata else {}
        result = create_snapshot(args.session_id, args.snapshot_id, args.paths, metadata)
    
    elif args.command == "restore":
        if not args.snapshot_id:
            print("Error: --snapshot-id required for restore", file=sys.stderr)
            sys.exit(1)
        success = restore_snapshot(args.session_id, args.snapshot_id, args.target_dir)
        result = {"success": success}
    
    elif args.command == "list":
        result = list_snapshots(args.session_id)
    
    elif args.command == "latest":
        result = get_latest_snapshot(args.session_id)
    
    elif args.command == "delete":
        if not args.snapshot_id:
            print("Error: --snapshot-id required for delete", file=sys.stderr)
            sys.exit(1)
        success = delete_snapshot(args.session_id, args.snapshot_id)
        result = {"success": success}
    
    elif args.command == "cleanup":
        deleted = cleanup_old_snapshots(args.session_id, args.keep)
        result = {"deleted": deleted}
    
    elif args.command == "rollback":
        success = rollback_to_snapshot(args.session_id, args.snapshot_id, args.target_dir)
        result = {"success": success}
    
    elif args.command == "auto":
        if not args.step or not args.paths:
            print("Error: --step and --paths required for auto", file=sys.stderr)
            sys.exit(1)
        metadata = json.loads(args.metadata) if args.metadata else {}
        snapshot_id = auto_snapshot_before_step(args.session_id, args.step, args.paths, metadata)
        result = {"snapshot_id": snapshot_id}
    
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result)


if __name__ == "__main__":
    main()
