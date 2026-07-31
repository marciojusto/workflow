#!/usr/bin/env python3
"""
install-state.py — Helper para gerenciar o state file do instalador.
"""
import json
import os
import sys

STATE_FILE = os.path.expanduser("~/.workflow-installer-state.json")


def load():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get(key, default=None):
    return load().get(key, default)


def set(key, value):
    state = load()
    state[key] = value
    save(state)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: install-state.py <get|set|load|save> [key] [value]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "load":
        print(json.dumps(load(), indent=2))
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
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
