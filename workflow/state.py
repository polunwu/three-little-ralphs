#!/usr/bin/env python3
"""State file read/write helper with file locking and git commit support.

Usage:
    python3 workflow/state.py read
    python3 workflow/state.py write '<json patch>' ['commit message']
"""

import fcntl
import json
import subprocess
import sys
from pathlib import Path

WORKFLOW_DIR = Path(__file__).parent
STATE_FILE = WORKFLOW_DIR / "state.json"
LOCK_FILE = WORKFLOW_DIR / "state.json.lock"
PROJECT_DIR = WORKFLOW_DIR.parent


def read_state():
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
    print(json.dumps(data, ensure_ascii=False, indent=2))


def write_state(patch_json, commit_message=None):
    with open(LOCK_FILE, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            current = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            patch = json.loads(patch_json)
            current.update(patch)
            STATE_FILE.write_text(
                json.dumps(current, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            if commit_message:
                rel_state = STATE_FILE.relative_to(PROJECT_DIR)
                subprocess.run(
                    ["git", "add", str(rel_state)],
                    cwd=PROJECT_DIR,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=PROJECT_DIR,
                    check=True,
                )
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: state.py read | write '<json>' ['commit message']",
            file=sys.stderr,
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "read":
        read_state()
    elif command == "write":
        if len(sys.argv) < 3:
            print("Usage: state.py write '<json>' ['commit message']", file=sys.stderr)
            sys.exit(1)
        patch_json = sys.argv[2]
        commit_message = sys.argv[3] if len(sys.argv) > 3 else None
        write_state(patch_json, commit_message)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
