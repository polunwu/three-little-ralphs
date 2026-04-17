---
shaping: true
---

# Claude Code 多角色工作流 v2 — Slices

## Slice 總覽

| # | Slice | Shape Part | Affordances | Demo |
|---|-------|------------|-------------|------|
| V1 | 目錄重整 | A2 | U3, U4, U5 | `ls workflow/agents/` 看到三個 agent 檔案 |
| V2 | start.sh 改版 | A1 | N1, N2, N3_init, U2 | `bash start.sh` 複製 settings 並印出三段指令；state.json task_list 有 `[ ]` 前綴 |
| V3 | 任務標記 | A4 | N6, N14, N15, N24, N25 | 任務跑完一輪後，tasks.md 從 `[ ]` → `[/]` → `[x]` |
| V4 | git 上下文 | A3 | N12, N22 | Reviewer session 顯示 `git show HEAD`；Judge session 顯示 `git log -p -3` |
| V5 | 實作摘要 | A5 | N8, S5 | Executor 完成後 `cat workflow/implementation_done.md` 看到新紀錄 |

依賴順序：V1 → V2 → V3；V4 和 V5 依賴 V1，彼此獨立。

---

## V1: 目錄重整

**Demo：** `ls workflow/agents/` 顯示 executor.md / reviewer.md / judge.md；工作流仍可正常執行。

**變更的檔案：**
- 建立 `workflow/agents/`，移入三個 agent .md 檔
- 建立 `workflow/skills/`（空目錄，加 `.gitkeep`）
- 更新 `CLAUDE.md` 中的路徑說明

**Affordances:**

| # | Affordance | Control | Wires Out | Returns To | 備註 |
|---|------------|---------|-----------|------------|------|
| U3 | workflow/agents/executor.md | read | — | → N3 | 路徑從 workflow/ 移至 workflow/agents/ |
| U4 | workflow/agents/reviewer.md | read | — | → N10 | 路徑從 workflow/ 移至 workflow/agents/ |
| U5 | workflow/agents/judge.md | read | — | → N20 | 路徑從 workflow/ 移至 workflow/agents/ |

---

## V2: start.sh 改版

**Demo：** `bash start.sh` 自動複製 settings；`python3 workflow/state.py read` 顯示 task_list 每項帶 `[ ]` 前綴；terminal 印出三段可直接貼上的啟動指令。

**變更的檔案：**
- 改寫 `workflow/start.sh`

**Affordances:**

| # | Affordance | Control | Wires Out | Returns To | 備註 |
|---|------------|---------|-----------|------------|------|
| U1 | `bash start.sh` | invoke | → N1 | — | 已有，入口不變 |
| N1 | `cp settings/agent-claude-settings.json .claude/settings.json` | call | → S3, → N2 | — | 新增 |
| N2 | 從 tasks.md 讀入任務，加 `[ ]` 前綴寫入 state.json task_list | call | → S1, → N3_init | — | 新增（取代舊 start.sh 初始化邏輯） |
| N3_init | 印出三段啟動指令（Judge → Reviewer → Executor） | call | → U2 | — | 新增 |
| U2 | 三段啟動指令 | render | — | — | 新增 |

---

## V3: 任務標記

**Demo：** 執行一個完整任務週期後，tasks.md 在實作完成時顯示 `[/]`，驗收通過後顯示 `[x]`；退回時清回 `[ ]`。

**變更的檔案：**
- 更新 `workflow/state.py`：每次寫入 state.json 時同步 tasks.md（依 task_list 重寫 tasks.md）
- 更新 `workflow/agents/executor.md`：完成 commit 後寫 state 時帶 `[/]` 前綴
- 更新 `workflow/agents/reviewer.md`：reject 時帶 `[ ]` 前綴
- 更新 `workflow/agents/judge.md`：accept 時帶 `[x]`、reject 時帶 `[ ]` 前綴

**Affordances:**

| # | Affordance | Control | Wires Out | Returns To | 備註 |
|---|------------|---------|-----------|------------|------|
| N6 | state.py: task_list[current] → `[/]`、task_status → 待審查（同步 tasks.md） | call | → S1, → S2, → N8 | — | 更新（加前綴 + tasks.md sync） |
| N14 | state.py: task_status → 待驗收（同步 tasks.md） | call | → S1, → S2 | — | 更新（加 tasks.md sync） |
| N15 | state.py: task_list[current] → `[ ]`、task_status → 待實作、retry_count++、reviewer_notes（同步 tasks.md） | call | → S1, → S2 | — | 更新（加前綴 + tasks.md sync） |
| N24 | state.py: task_list[current] → `[x]`、advance current_task_index、reset retry_count（同步 tasks.md） | call | → S1, → S2 | — | 更新（加前綴 + tasks.md sync） |
| N25 | state.py: task_list[current] → `[ ]`、task_status → 待實作、retry_count++、judge_notes（同步 tasks.md） | call | → S1, → S2 | — | 更新（加前綴 + tasks.md sync） |

---

## V4: git 上下文

**Demo：** Reviewer 的 loop session 在確認輪到自己後印出 `git show HEAD` 結果；Judge session 印出 `git log -p -3` 結果，然後才開始審查/驗收。

**變更的檔案：**
- 更新 `workflow/agents/reviewer.md`：在確認 task_status == 待審查 後、開始審查前，執行 `git show HEAD`
- 更新 `workflow/agents/judge.md`：在確認 task_status == 待驗收 後、開始驗收前，執行 `git log -p -3`

**Affordances:**

| # | Affordance | Control | Wires Out | Returns To | 備註 |
|---|------------|---------|-----------|------------|------|
| N12 | `git show HEAD` | call | — | → N13 | 新增（插入 N11 與 N13 之間） |
| N22 | `git log -p -3` | call | — | → N23 | 新增（插入 N21 與 N23 之間） |

---

## V5: 實作摘要

**Demo：** Executor 完成一個任務後，`cat workflow/implementation_done.md` 顯示新增一筆紀錄，包含日期時間、任務名稱、摘要、files changed、commit hash。

**變更的檔案：**
- 更新 `workflow/agents/executor.md`：git commit 後、寫 state 前，append 一筆摘要至 `workflow/implementation_done.md`

**Affordances:**

| # | Affordance | Control | Wires Out | Returns To | 備註 |
|---|------------|---------|-----------|------------|------|
| N8 | Append to implementation_done.md（日期時間、任務名稱、摘要 ≤200字、files changed、commit hash） | call | → S5 | — | 新增（N5 → N6 之間） |
| S5 | workflow/implementation_done.md | write | — | — | 新增 |
