# 操作手冊

---

## 多角色工作流（Executor / Reviewer / Judge）

### 第一次使用（複製 workflow 到新專案）

把 `workflow/` 資料夾整個複製到目標專案根目錄即可。

### 每次執行

**步驟 1：填任務**

編輯 `workflow/tasks.md`，每行 `- ` 開頭寫一個任務：

```markdown
- 實作登入 API，接受帳號密碼，回傳 JWT token
- 實作登出 API，清除 session
```

**步驟 2：初始化**

在專案根目錄執行：

```bash
bash workflow/start.sh
```

輸出會印出三個終端機指令。

**步驟 3：啟動三個角色**

`sbx run` 不支援透傳參數給 claude，須先建立 sandbox，再用 `sbx exec` 進入執行。開四個終端機：

```bash
# Terminal 1 — 建立 sandbox（可用於監控 / 手動查詢狀態）
cd test-todo-project
sbx run claude

# Terminal 2 — Executor
sbx run claude
# 然後輸入：/loop 1min 執行 workflow/executor.md 的工作

# Terminal 3 — Reviewer
sbx run claude
# 然後輸入：/loop 1min 執行 workflow/reviewer.md 的工作

# Terminal 4 — Judge
sbx run claude
# 然後輸入：/loop 1min 執行 workflow/judge.md 的工作
```

**步驟 4：監控狀態**

```bash
python3 workflow/state.py read
```

### 系統暫停（waiting_for_user）

Reviewer 或 Judge 退回任務超過 3 次、或 Judge 偵測到執行偏離時，`system_status` 會變成 `waiting_for_user`，三個角色都會停止動作。

查看 `reviewer_notes` 或 `judge_notes` 了解原因：

```bash
python3 workflow/state.py read
```

處理完畢後，手動將 `system_status` 改回 `running` 恢復執行：

```bash
python3 workflow/state.py write '{"system_status": "running"}'
```

若需要動態新增任務（V5 偏離情境），先編輯 `state.json` 的 `task_list`，再恢復 `system_status`。

---

## sbx + agent

```bash
cp settings/agent-claude-settings.json .claude/settings.json
sbx run claude
```

```bash
./claude.sh sbx
```

> 如果 settings 出錯，先 `sbx rm <sandbox-name>` 再重跑。
