#!/bin/bash
set -euo pipefail

WORKFLOW_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_FILE="$WORKFLOW_DIR/state.json"
TEMPLATE_FILE="$WORKFLOW_DIR/state.json.template"
TASKS_FILE="$WORKFLOW_DIR/tasks.md"

# Parse tasks.md and generate state.json
python3 - "$TASKS_FILE" "$TEMPLATE_FILE" "$STATE_FILE" <<'PYEOF'
import json
import sys

tasks_file, template_file, state_file = sys.argv[1], sys.argv[2], sys.argv[3]

with open(tasks_file, encoding="utf-8") as f:
    lines = f.readlines()

tasks = [line[2:].strip() for line in lines if line.startswith("- ") and line[2:].strip()]

if not tasks:
    print("錯誤：tasks.md 中找不到任何任務（格式：'- 任務描述'）", file=sys.stderr)
    sys.exit(1)

with open(template_file, encoding="utf-8") as f:
    state = json.load(f)

state["task_list"] = tasks

with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"✓ 已載入 {len(tasks)} 個任務：")
for i, t in enumerate(tasks):
    print(f"  [{i}] {t}")
PYEOF

echo ""
echo "✓ state.json 初始化完成。請在三個獨立終端機中分別執行以下指令："
echo ""
echo "  ┌─ Executor ───────────────────────────────────────────────────────────┐"
echo "  │  cd $(dirname "$WORKFLOW_DIR")                                       │"
echo "  │  sbx run claude                                                      │"
echo "  │  然後輸入：/loop 1min 執行 workflow/executor.md 的工作               │"
echo "  └──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  ┌─ Reviewer ───────────────────────────────────────────────────────────┐"
echo "  │  cd $(dirname "$WORKFLOW_DIR")                                       │"
echo "  │  sbx run claude                                                      │"
echo "  │  然後輸入：/loop 1min 執行 workflow/reviewer.md 的工作               │"
echo "  └──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  ┌─ Judge ──────────────────────────────────────────────────────────────┐"
echo "  │  cd $(dirname "$WORKFLOW_DIR")                                       │"
echo "  │  sbx run claude                                                      │"
echo "  │  然後輸入：/loop 1min 執行 workflow/judge.md 的工作                  │"
echo "  └──────────────────────────────────────────────────────────────────────┘"
echo ""
echo "  完成後可用 python3 workflow/state.py read 查看目前狀態。"
