---
shaping: true
---

# Claude Code 多角色工作流 — Slices

## Slice Summary

| # | Slice | 機制 | Demo |
|---|-------|------|------|
| V1 | State File + Executor 跑起來 | A1, A2 | Executor 讀取任務、實作程式碼、State File 的 task_status 變成「待審查」 |
| V2 | Reviewer 通過路徑 | A3（pass） | Reviewer 審查通過，task_status 變成「待驗收」 |
| V3 | Judge 通過 + 推進任務 | A4（pass） | Judge 驗收通過，推進下一個任務；全部任務完成後停止 |
| V4 | 退回 + 重試 + 暫停/恢復 | A3（fail）、A4（fail）、A5 | 任務被退回 3 次，系統暫停並寫入說明；User 修改 State File 後恢復執行 |
| V5 | 偏離偵測 + 動態新增確認 | A4（deviation）、A6 | Judge 偵測偏離通報 User；User 確認動態新增任務後系統繼續 |

---

## V1：State File + Executor 跑起來

**Demo：** Executor 讀取第一個任務，實作程式碼，State File 的 task_status 變成「待審查」

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| S1 | task_list | init | — | → N2 |
| S2 | current_task_index | init | — | → N2 |
| S3 | task_status | init | — | → N1 |
| S4 | retry_count | init | — | — |
| S5 | system_status | init | — | → N1 |
| S6 | reviewer_notes | init | — | → U1 |
| S7 | judge_notes | init | — | → U1 |
| N1 | poll() | call | → N2（若 running + 待實作） | — |
| N2 | read_task() | call | → N3 | — |
| N3 | execute() | call | → N4 | — |
| N4 | write task_status → "待審查" | write | → S3 | — |
| U1 | 讀 State File（status + notes） | read | — | — |

---

## V2：Reviewer 通過路徑

**Demo：** Reviewer 看到 task_status=待審查，審查通過，task_status 變成「待驗收」

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N10 | poll() | call | → N11（若 running + 待審查） | — |
| N11 | read_task_and_code() | call | → N12 | — |
| N12 | review() | call | → N13 | — |
| N13 | write task_status → "待驗收" | write | → S3 | — |

---

## V3：Judge 通過 + 推進任務

**Demo：** Judge 看到 task_status=待驗收，驗收通過，推進下一個任務；全部任務完成後 system_status → done

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N20 | poll() | call | → N21（若 running + 待驗收） | — |
| N21 | read_task_and_result() | call | → N22 | — |
| N22 | validate() | call | → N23 | — |
| N23 | advance：write index++, status → "待實作", retry → 0 | write | → S2, S3, S4 | — |

---

## V4：退回 + 重試 + 暫停/恢復

**Demo：** 任務被退回 3 次，system_status 變成 waiting_for_user 並附說明；User 直接編輯 State File 將 system_status 改回 running，系統恢復執行

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N14 | write task_status → "待實作", retry++, reviewer_notes | write | → S3, S4, S6 | — |
| N15 | write system_status → "waiting_for_user" | write | → S5 | — |
| N24 | write task_status → "待實作", retry++ | write | → S3, S4 | — |
| N25 | write system_status → "waiting_for_user", judge_notes | write | → S5, S7 | — |
| U2 | 寫 system_status → "running"（恢復執行） | write | → S5 | — |

N14 → N15（若 S4 ≥ 3）
N24 → N25（若 S4 ≥ 3）

---

## V5：偏離偵測 + 動態新增確認

**Demo：** Judge 偵測到執行偏離任務定義，寫入 waiting_for_user + judge_notes；User 確認後動態新增任務並恢復執行

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N22（deviation） | detect_deviation() → N25 | call | → N25 | — |
| U3 | 確認並寫入新任務至 task_list | write | → S1 | — |
