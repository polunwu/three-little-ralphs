---
shaping: true
---

# Claude Code 多角色工作流 v2 — Shaping

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | `start.sh` 自動複製 `settings/agent-claude-settings.json` 到 `.claude/settings.json`，並依序印出三段啟動指令（Judge → Reviewer → Executor），貼進 terminal 即可執行 | Must-have |
| R1 | Reviewer 確定輪到自己後執行 `git show HEAD`；Judge 執行 `git log -p -3`；Executor 不需要 | Must-have |
| R2 | 建立 `workflow/agents/`，將 executor.md / reviewer.md / judge.md 移入；建立空的 `workflow/skills/`（留給未來） | Must-have |
| R3 | state.json `task_list` 項目帶 `[ ]`/`[/]`/`[x]` 前綴作為唯一標記來源；state.py 每次寫入時同步 tasks.md；start.sh 初始化時從 tasks.md 讀入並加 `[ ]` 前綴；Executor 標 `[/]`、Judge 標 `[x]`、退回清 `[ ]` | Must-have |
| R3b | Executor 每次 commit 後 append 一筆紀錄至 `workflow/implementation_done.md`（日期時間、任務名稱、摘要 ≤200字、files changed、commit hash） | Must-have |
| R4 | v1 核心狀態機邏輯（state.json 結構、三角色流轉）保持不變 | Must-have |

延後（明確排出本輪）：
- tmux 一鍵啟動三角色 → v3 研究

---

## A: v2 四項改進

| Part | Mechanism |
|------|-----------|
| **A1** | **start.sh 改版** — 自動複製 `settings/agent-claude-settings.json` 到 `.claude/settings.json`，完成後依序印出三段啟動指令（Judge → Reviewer → Executor） |
| **A2** | **目錄重整** — 建立 `workflow/agents/`，將 executor.md / reviewer.md / judge.md 移入；建立空的 `workflow/skills/`（留給未來） |
| **A3** | **Agent prompt 加 git 上下文** — Reviewer 確認輪到自己後執行 `git show HEAD`；Judge 執行 `git log -p -3`；Executor 不需要（自己寫的） |
| **A4** | **任務標記** — state.json `task_list` 為唯一標記來源；Executor 實作完後標 `[/]`、Judge 驗收通過後改 `[x]`、退回清 `[ ]`；state.py 每次寫入時同步 tasks.md；start.sh 初始化時從 tasks.md 讀入並加 `[ ]` 前綴 |
| **A5** | **實作摘要紀錄** — Executor commit 後 append 至 `workflow/implementation_done.md`：日期時間、任務名稱、摘要（≤200字）、files changed、commit hash |

---

## Fit Check: R × A

| Req | Requirement | Status | A |
|-----|-------------|--------|---|
| R0 | start.sh 自動複製 settings，並依序印出三段啟動指令 | Must-have | ✅ |
| R1 | Reviewer: git show HEAD；Judge: git log -p -3；Executor: 不需要 | Must-have | ✅ |
| R2 | workflow/agents/ + workflow/skills/ 巢狀分層 | Must-have | ✅ |
| R3 | state.json task_list 帶前綴為唯一來源；state.py 同步 tasks.md；start.sh 初始化加 [ ] 前綴 | Must-have | ✅ |
| R3b | Executor commit 後 append 至 implementation_done.md | Must-have | ✅ |
| R4 | 核心狀態機邏輯不變 | Must-have | ✅ |

**Selected shape: A**
