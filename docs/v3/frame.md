---
shaping: true
---

# Workflow v3 — Frame

## Source

### polunwu (docs/ideas.md)

> - gitignore test-todo-project
> - start.sh 獨立出 python 的腳本
> - 拆成四個 .sh 腳本: setup, judge, reviewer, excutor 把要做的事塞到指令裡，loop, 執行 agent.md, 指定模型
> - 整理多個檔案成 README.md

---

## Pre-work: v3 Improvement Options

4 improvements surfaced. Each addresses a distinct friction point in the current workflow:

| Option | What it does | Who benefits | Signal strength |
|--------|-------------|--------------|-----------------|
| **A. .gitignore test-todo-project** | Stop tracking the reference project in git | Anyone cloning or copying the workflow | Low friction to fix; unambiguous |
| **B. Extract Python from start.sh** | Move inline heredoc Python to a standalone `init_state.py` | Anyone editing or debugging task initialization logic | Medium — code currently buried inside a bash heredoc |
| **C. Four launcher scripts** | Replace manual `/loop` typing inside sbx with one-command launchers per agent | Anyone running the workflow — reduces steps each time | High — most repeated friction per run |
| **D. Consolidate docs into README.md** | Merge `RUNBOOK.md`, `setup-sbx.md`, relevant `CLAUDE.md` sections into one file | New users and anyone returning to the workflow after a break | Medium — fragmentation causes confusion on where to look |

**Why all four, together:** These are not competing alternatives — they address separate concerns (git hygiene, code maintainability, launch UX, documentation). None blocks the others. The natural order: A and D are housekeeping; B is a prerequisite for clean launcher scripts; C is the highest-friction item and the goal of the v3 effort.

---

## Problem

- `test-todo-project/` is tracked by git with no `.gitignore`, even though it's a test fixture not part of the workflow artifact
- `start.sh` embeds ~60 lines of Python as a heredoc, making the task-parsing logic hard to read, edit, or test independently
- Launching each agent requires: (1) open a terminal, (2) run `sbx run claude`, (3) wait for the session to open, (4) manually type the `/loop` command with the right agent path — three steps that must be repeated for all three agents each run
- Workflow documentation is split across `RUNBOOK.md`, `setup-sbx.md`, and `CLAUDE.md` — no single file tells a new user how to set up and run the workflow

## Outcome

- Cloning or copying the `workflow/` directory does not pull in `test-todo-project/` noise
- Task initialization logic lives in its own file and can be read, edited, or tested without parsing bash
- Running an agent is a single command — model, loop interval, and agent path are pre-configured
- One `README.md` covers setup and usage; old doc files are removed
