# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A sandbox for experimenting with **multi-agent Claude Code workflows** running inside Docker Sandboxes (`sbx`). The main artifact is a reusable `workflow/` directory that can be dropped into any project to orchestrate three specialized Claude agents (Executor, Reviewer, Judge) running in parallel loops.

`test-todo-project/` is the reference project used to validate the workflow — a minimal Python CLI todo app.

---

## Running the Multi-Agent Workflow

### Setup (first time for a new project)

Copy `workflow/` into the target project root.

### Each run

**1. Define tasks** — edit `workflow/tasks.md`, one task per `- ` bullet line.

**2. Initialize state:**

```bash
bash workflow/start.sh
```

**3. Launch four terminals** (each uses `sbx run claude` because `sbx run` doesn't pass args to claude directly):

```bash
# Terminal 1 — monitor / sandbox host
cd test-todo-project && sbx run claude

# Terminal 2 — Executor
sbx run claude
# Then type: /loop 1min 執行 workflow/executor.md 的工作

# Terminal 3 — Reviewer
sbx run claude
# Then type: /loop 1min 執行 workflow/reviewer.md 的工作

# Terminal 4 — Judge
sbx run claude
# Then type: /loop 1min 執行 workflow/judge.md 的工作
```

**4. Monitor state:**

```bash
python3 workflow/state.py read
```

**5. Resume after a pause** (`system_status` becomes `waiting_for_user` after 3 retries or deviation):

```bash
python3 workflow/state.py write '{"system_status": "running"}'
```

### Shortcut: apply agent settings and launch sbx in one command

```bash
./claude.sh sbx
```

---

## Workflow Architecture

State is managed in `workflow/state.json` (created from `state.json.template` by `start.sh`). The three agents coordinate exclusively through this file — they never communicate directly.

**State fields:**

- `system_status`: `running` | `waiting_for_user` | `done`
- `task_status`: `待實作` | `待審查` | `待驗收` | `完成`
- `current_task_index`: index into `task_list`
- `retry_count`: increments on each reject; triggers pause at ≥ 3
- `reviewer_notes` / `judge_notes`: rejection reasons written by each agent

**Agent responsibilities:**

- **Executor** (`workflow/executor.md`): acts when `task_status == "待實作"` — implements code, commits, advances status to `"待審查"`
- **Reviewer** (`workflow/reviewer.md`): acts when `task_status == "待審查"` — reviews code quality and requirements fit; passes to `"待驗收"` or rejects back to `"待實作"`
- **Judge** (`workflow/judge.md`): acts when `task_status == "待驗收"` — checks for deviation (changes outside task scope), accepts and advances to next task or rejects

`workflow/state.py` handles file-locking (`fcntl`) and optional git commits atomically.

---

## Docker Sandbox (`sbx`) Setup

See `setup-sbx.md` for full install instructions. Quick reference:

```bash
brew install docker/tap/sbx
sbx login
```

Key `sbx` commands: `sbx run claude`, `sbx ls`, `sbx stop <name>`, `sbx rm <name>`, `sbx exec -it <name> bash`

**Branch mode** (for multi-agent parallel runs to avoid conflicts):

```bash
sbx run --branch auto claude
```

**Port forwarding note:** services inside sandbox must bind to `0.0.0.0`; access host services via `host.docker.internal`.

---

## Agent Settings

`settings/agent-claude-settings.json` is the locked-down permission profile for agents running inside `sbx`. It blocks: reading/writing `.env` files, `rm -rf`, `sudo`, `git push`, and writes to `*.production.*` / `*.prod.*` files.

`./claude.sh sbx` copies this file to `.claude/settings.json` before launching the sandbox.

---

## Test Todo Project

Located in `test-todo-project/`. Python 3.6+, no dependencies. Data stored in `~/.todos.txt`.

```bash
python3 todo.py add "task"
python3 todo.py list
python3 todo.py done <id>
python3 todo.py delete <id>
python3 todo.py clear
```

Run tests:

```bash
python3 -m unittest test_todo -v
```
