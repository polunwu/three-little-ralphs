#!/bin/bash
set -euo pipefail

WORKFLOW_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$WORKFLOW_DIR")"
STATE_FILE="$WORKFLOW_DIR/state.json"
TEMPLATE_FILE="$WORKFLOW_DIR/state.json.template"
TASKS_FILE="$WORKFLOW_DIR/tasks.md"
SETTINGS_SRC="$WORKFLOW_DIR/settings/agent-claude-settings.json"
SETTINGS_DST="$PROJECT_DIR/.claude/settings.json"

# Copy agent settings
if [ -f "$SETTINGS_SRC" ]; then
    mkdir -p "$(dirname "$SETTINGS_DST")"
    cp "$SETTINGS_SRC" "$SETTINGS_DST"
    echo "✓ agent settings 已複製至 .claude/settings.json"
else
    echo "⚠ 找不到 $SETTINGS_SRC，跳過 settings 複製"
fi

# Parse tasks.md, add [ ] prefix, and generate state.json
python3 - "$TASKS_FILE" "$TEMPLATE_FILE" "$STATE_FILE" <<'PYEOF'
import json
import sys

tasks_file, template_file, state_file = sys.argv[1], sys.argv[2], sys.argv[3]

with open(tasks_file, encoding="utf-8") as f:
    lines = f.readlines()

tasks_raw = []
for line in lines:
    stripped = line.strip()
    is_task = stripped.startswith("- ") or any(stripped.startswith(p) for p in ("[ ] ", "[/] ", "[x] "))
    if not is_task:
        continue
    if stripped.startswith("- "):
        stripped = stripped[2:].strip()
    # Strip existing marker prefixes if re-initializing
    for prefix in ("[ ] ", "[/] ", "[x] "):
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    if stripped:
        tasks_raw.append(stripped)

if not tasks_raw:
    print("錯誤：tasks.md 中找不到任何任務（格式：'- 任務描述'）", file=sys.stderr)
    sys.exit(1)

tasks = [f"[ ] {t}" for t in tasks_raw]

with open(template_file, encoding="utf-8") as f:
    state = json.load(f)

state["task_list"] = tasks

with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

# Sync tasks.md: preserve non-task lines, update task lines with [ ] prefix
new_lines = []
task_iter = iter(tasks)
for line in lines:
    stripped = line.strip()
    if stripped.startswith("- ") or any(stripped.startswith(p) for p in ("[ ] ", "[/] ", "[x] ")):
        try:
            new_lines.append(next(task_iter) + "\n")
        except StopIteration:
            pass
    else:
        new_lines.append(line)
with open(tasks_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"✓ 已載入 {len(tasks)} 個任務：")
for i, t in enumerate(tasks):
    print(f"  [{i}] {t}")
PYEOF

echo ""
echo "✓ state.json 初始化完成。請依序在三個獨立終端機中執行以下指令："
echo ""
echo "  ┌─ 1. Judge ───────────────────────────────────────────────────────────────┐"
echo "  │  cd $PROJECT_DIR                                                         │"
echo "  │  sbx run claude                                                          │"
echo "  │  然後輸入：/loop 1min 執行 workflow/agents/judge.md 的工作                │"
echo "  └──────────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  ┌─ 2. Reviewer ────────────────────────────────────────────────────────────┐"
echo "  │  cd $PROJECT_DIR                                                         │"
echo "  │  sbx run claude                                                          │"
echo "  │  然後輸入：/loop 1min 執行 workflow/agents/reviewer.md 的工作             │"
echo "  └──────────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  ┌─ 3. Executor ────────────────────────────────────────────────────────────┐"
echo "  │  cd $PROJECT_DIR                                                         │"
echo "  │  sbx run claude                                                          │"
echo "  │  然後輸入：/loop 1min 執行 workflow/agents/executor.md 的工作             │"
echo "  └──────────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  完成後可用 python3 workflow/state.py read 查看目前狀態。"
