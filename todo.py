#!/usr/bin/env python3
"""CLI Todo List - simple plain-text task manager."""

import argparse
import sys
from pathlib import Path

TODO_FILE = Path.home() / ".todos.txt"

# ANSI colors
GREEN = "\033[32m"
RED = "\033[31m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"


def load_todos():
    if not TODO_FILE.exists():
        return []
    lines = TODO_FILE.read_text(encoding="utf-8").splitlines()
    todos = []
    for i, line in enumerate(lines, start=1):
        if line.startswith("[x] "):
            todos.append({"id": i, "done": True, "text": line[4:]})
        elif line.startswith("[ ] "):
            todos.append({"id": i, "done": False, "text": line[4:]})
    return todos


def save_todos(todos):
    lines = []
    for t in todos:
        prefix = "[x] " if t["done"] else "[ ] "
        lines.append(prefix + t["text"])
    TODO_FILE.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def cmd_list():
    todos = load_todos()
    if not todos:
        print(f"{GRAY}沒有任何 todo。用 'todo add \"任務\"' 新增一筆。{RESET}")
        return
    for t in todos:
        if t["done"]:
            status = f"{GREEN}[✓]{RESET}"
            text = f"{GRAY}{t['text']}{RESET}"
        else:
            status = f"[ ]"
            text = t["text"]
        print(f"  {BOLD}{t['id']:>3}{RESET}  {status}  {text}")


def cmd_add(text):
    text = text.strip()
    if not text:
        print(f"{RED}錯誤：任務內容不能為空。{RESET}", file=sys.stderr)
        sys.exit(1)
    with TODO_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[ ] {text}\n")
    print(f"{GREEN}✓ 已新增：{text}{RESET}")


def cmd_done(id_):
    todos = load_todos()
    matched = [t for t in todos if t["id"] == id_]
    if not matched:
        print(f"{RED}錯誤：找不到 ID {id_}。{RESET}", file=sys.stderr)
        sys.exit(1)
    todo = matched[0]
    if todo["done"]:
        print(f"{GRAY}ID {id_} 已經是完成狀態：{todo['text']}{RESET}")
        return
    todo["done"] = True
    save_todos(todos)
    print(f"{GREEN}✓ 已完成：{todo['text']}{RESET}")


def cmd_delete(id_):
    todos = load_todos()
    matched = [t for t in todos if t["id"] == id_]
    if not matched:
        print(f"{RED}錯誤：找不到 ID {id_}。{RESET}", file=sys.stderr)
        sys.exit(1)
    todo = matched[0]
    remaining = [t for t in todos if t["id"] != id_]
    save_todos(remaining)
    print(f"{RED}✓ 已刪除：{todo['text']}{RESET}")


def cmd_clear():
    todos = load_todos()
    done_count = sum(1 for t in todos if t["done"])
    if done_count == 0:
        print(f"{GRAY}沒有已完成的項目可以清除。{RESET}")
        return
    remaining = [t for t in todos if not t["done"]]
    save_todos(remaining)
    print(f"{GREEN}✓ 已清除 {done_count} 筆已完成的項目。{RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="todo",
        description="簡單的 CLI Todo List",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="列出所有 todo")

    p_add = subparsers.add_parser("add", help="新增一筆 todo")
    p_add.add_argument("text", help="任務內容")

    p_done = subparsers.add_parser("done", help="標記為已完成")
    p_done.add_argument("id", type=int, help="Todo ID")

    p_delete = subparsers.add_parser("delete", aliases=["del", "rm"], help="刪除指定 todo")
    p_delete.add_argument("id", type=int, help="Todo ID")

    subparsers.add_parser("clear", help="清除所有已完成的項目")

    args = parser.parse_args()

    if args.command in (None, "list"):
        cmd_list()
    elif args.command == "add":
        cmd_add(args.text)
    elif args.command == "done":
        cmd_done(args.id)
    elif args.command in ("delete", "del", "rm"):
        cmd_delete(args.id)
    elif args.command == "clear":
        cmd_clear()


if __name__ == "__main__":
    main()
