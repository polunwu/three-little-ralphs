# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A minimal CLI todo list in Python. No external dependencies — just the standard library. Data is stored in `~/.todos.txt` as plain text.

## Commands

Run the app:
```bash
python3 todo.py <command> [args]
# Commands: list, add "<text>", done <id>, delete <id>, clear
```

Run all tests:
```bash
python3 -m unittest test_todo -v
```

Run a single test class or method:
```bash
python3 -m unittest test_todo.TestAdd -v
python3 -m unittest test_todo.TestAdd.test_add_single -v
```

## Architecture

All logic lives in two files:

- `todo.py` — the entire application: data model, file I/O, command functions, and CLI wiring via `argparse`
- `test_todo.py` — full test suite using `unittest`

**Data model**: todos are plain dicts `{"id": int, "done": bool, "text": str}`. IDs are 1-based line numbers derived at load time from `~/.todos.txt` — they are positional, not stable. After a delete, remaining items are re-indexed on the next load.

**File format**: one task per line — `[ ] text` (pending) or `[x] text` (done). The file is rewritten in full on every `done`, `delete`, or `clear` operation; `add` appends a single line.

**Test isolation**: `TodoTestCase` base class monkey-patches `todo.TODO_FILE` to a `NamedTemporaryFile` in `setUp`/`tearDown`, so tests never touch `~/.todos.txt`.
