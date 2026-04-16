#!/usr/bin/env python3
"""State file read/write helper with file locking and git commit support.

Usage:
    python3 workflow/state.py read
    python3 workflow/state.py write '<json patch>' ['commit message']

On every write, state.py automatically:
  - Updates task_list[current_task_index] marker based on task_status transition:
      task_status → "待審查"       : marker → [/]
      task_status → "待實作" (reject) : marker → [ ]
      current_task_index advances    : old task marker → [x]
      system_status → "done"         : marker → [x]
  - Syncs tasks.md from task_list
"""

import fcntl
import json
import subprocess
import sys
from pathlib import Path

WORKFLOW_DIR = Path(__file__).parent
STATE_FILE = WORKFLOW_DIR / "state.json"
LOCK_FILE = WORKFLOW_DIR / "state.json.lock"
TASKS_FILE = WORKFLOW_DIR / "tasks.md"
PROJECT_DIR = WORKFLOW_DIR.parent

MARKER_PREFIXES = ("[ ] ", "[/] ", "[x] ")


def _strip_marker(task):
    for prefix in MARKER_PREFIXES:
        if task.startswith(prefix):
            return task[len(prefix):]
    return task


def _set_marker(task_list, index, marker):
    if 0 <= index < len(task_list):
        task_list[index] = f"{marker} {_strip_marker(task_list[index])}"


def _update_task_marker(current, patch):
    """Infer and apply task_list marker change from the state transition."""
    task_list = current.get("task_list", [])
    if not task_list:
        return

    prev_index = current.get("current_task_index", 0)
    new_index = patch.get("current_task_index", prev_index)

    if new_index != prev_index:
        # Task advanced: mark completed task as [x]
        _set_marker(task_list, prev_index, "[x]")
    elif patch.get("system_status") == "done":
        # All tasks done: mark last task as [x]
        _set_marker(task_list, prev_index, "[x]")
    elif patch.get("task_status") == "待審查":
        # Executor completed: mark as [/]
        _set_marker(task_list, prev_index, "[/]")
    elif patch.get("task_status") == "待實作":
        # Rejection or pause: mark as [ ]
        _set_marker(task_list, prev_index, "[ ]")

    current["task_list"] = task_list


def _sync_tasks_md(state):
    """Sync tasks.md from state.json task_list."""
    task_list = state.get("task_list", [])
    TASKS_FILE.write_text(
        "".join(task + "\n" for task in task_list),
        encoding="utf-8",
    )


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
            _update_task_marker(current, patch)
            current.update(patch)
            STATE_FILE.write_text(
                json.dumps(current, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            _sync_tasks_md(current)
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
