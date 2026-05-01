---
shaping: true
---

# Claude Code 多角色工作流 — Shaping

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | 系統能自動執行一份任務列表，直到全部完成，無需人介入 | Core goal |
| R1 | 三個角色各自擁有獨立的 context window，互不污染 | Must-have |
| R2 | 任務進度與狀態持久化在共享文件中，任何角色都可以讀取當前狀態 | Must-have |
| R3 | Reviewer 審查程式碼品質與任務需求符合度；不通過則退回 Executor | Must-have |
| R4 | Judge 驗收任務需求符合度，並負責任務調度與通報使用者 | Must-have |
| R5 | 任務列表需在執行前定義完成；執行中動態新增需經使用者確認 | Must-have |
| R6 | Judge 偵測到執行偏離任務定義時，暫停並通知使用者確認後再繼續 | Must-have |
| R7 | Executor 單一任務最多退回重做 3 次；超過後暫停並通報使用者目前情況 | Must-have |
| R8 | 系統針對寫程式任務設計（Executor 具備程式碼讀寫能力） | Must-have |

---

## A: 三角色狀態機 + 共享 State File

| Part | Mechanism |
|------|-----------|
| A1 | **State File** — 存放 task_list、current_task_index、task_status、retry_count、system_status、reviewer_notes、judge_notes；所有角色與使用者皆可讀寫 |
| A2 | **Executor** — 讀取 State，若 system_status=running 且 task_status=待實作則執行，完成後更新 task_status → 待審查 |
| A3 | **Reviewer** — 讀取 State，若 system_status=running 且 task_status=待審查則審查程式碼品質與需求符合度；通過更新為待驗收，否則退回並附 reviewer_notes、遞增 retry_count；retry ≥ 3 時寫入 waiting_for_user |
| A4 | **Judge** — 讀取 State，若 system_status=running 且 task_status=待驗收則驗收；通過推進下一任務並重置 retry_count；不通過退回；retry ≥ 3 或偵測偏離時寫入 waiting_for_user + judge_notes |
| A5 | **Loop 協調** — 三個角色各自以 loop 輪詢 State File；system_status=waiting_for_user 時所有角色暫停，直到使用者將 system_status 改回 running |
| A6 | **動態新增確認** — 動態新增任務時，Judge 將 system_status 設為 waiting_for_user 並附說明，待使用者確認寫入 task_list 後才恢復執行 |

---

## Fit Check: R × A

| Req | Requirement | Status | A |
|-----|-------------|--------|---|
| R0 | 系統能自動執行一份任務列表，直到全部完成，無需人介入 | Core goal | ✅ |
| R1 | 三個角色各自擁有獨立的 context window，互不污染 | Must-have | ✅ |
| R2 | 任務進度與狀態持久化在共享文件中，任何角色都可以讀取當前狀態 | Must-have | ✅ |
| R3 | Reviewer 審查程式碼品質與任務需求符合度；不通過則退回 Executor | Must-have | ✅ |
| R4 | Judge 驗收任務需求符合度，並負責任務調度與通報使用者 | Must-have | ✅ |
| R5 | 任務列表需在執行前定義完成；執行中動態新增需經使用者確認 | Must-have | ✅ |
| R6 | Judge 偵測到執行偏離任務定義時，暫停並通知使用者確認後再繼續 | Must-have | ✅ |
| R7 | Executor 單一任務最多退回重做 3 次；超過後暫停並通報使用者目前情況 | Must-have | ✅ |
| R8 | 系統針對寫程式任務設計（Executor 具備程式碼讀寫能力） | Must-have | ✅ |

**Selected shape: A**

---

## Breadboard

見 `breadboard.md`
