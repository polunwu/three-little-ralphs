---
shaping: true
---

# Claude Code 多角色工作流 v2 — Breadboard

## Places

| # | Place | Description |
|---|-------|-------------|
| P1 | User Terminal | 執行 start.sh，開啟三個 agent session |
| P2 | Executor Loop | Executor 的 /loop sbx session |
| P3 | Reviewer Loop | Reviewer 的 /loop sbx session |
| P4 | Judge Loop | Judge 的 /loop sbx session |

## Data Stores

| # | Store | Description |
|---|-------|-------------|
| S1 | state.json | task_status、retry_count、system_status、task_list（帶 `[ ]`/`[/]`/`[x]` 前綴）、notes |
| S2 | tasks.md | 由 state.py 同步自 state.json task_list（agents 不直接寫入） |
| S3 | .claude/settings.json | Agent 權限設定 |
| S4 | git history | Executor commit 的程式碼變更 |
| S5 | workflow/implementation_done.md | Executor 實作摘要（append-only，僅供使用者查閱） |

## UI Affordances

| # | Place | Affordance | Control | Wires Out | Returns To |
|---|-------|------------|---------|-----------|------------|
| U1 | P1 | `bash start.sh` | invoke | → N1 | — |
| U2 | P1 | 三段啟動指令（Judge / Reviewer / Executor 順序） | render | — | — |
| U3 | P2 | workflow/agents/executor.md | read | — | → N3 |
| U4 | P3 | workflow/agents/reviewer.md | read | — | → N10 |
| U5 | P4 | workflow/agents/judge.md | read | — | → N20 |

## Code Affordances

### P1 — start.sh

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N1 | `cp settings/agent-claude-settings.json .claude/settings.json` | call | → S3, → N2 | — |
| N2 | 從 tasks.md 讀入任務，加 `[ ]` 前綴寫入 state.json task_list | call | → S1, → N3_init | — |
| N3_init | 印出三段啟動指令（順序：Judge → Reviewer → Executor） | call | → U2 | — |

### P2 — Executor Loop

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N3 | 讀取 state.json | call | — | → N4 |
| N4 | system_status == running AND task_status == 待實作? | conditional | → N5（yes）/ → N3（no，等下輪） | — |
| N5 | 實作程式碼 + git commit | call | → S4, → N6 | — |
| N6 | state.py: task_list[current] → `[/]`、task_status → 待審查（同步 tasks.md） | call | → S1, → S2, → N8 | — |
| N8 | Append to implementation_done.md（日期時間、任務名稱、摘要 ≤200字、files changed、commit hash） | call | → S5 | — |

### P3 — Reviewer Loop

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N10 | 讀取 state.json | call | — | → N11 |
| N11 | system_status == running AND task_status == 待審查? | conditional | → N12（yes）/ → N10（no，等下輪） | — |
| N12 | `git show HEAD` | call | — | → N13 |
| N13 | 審查程式碼品質與任務符合度 | call | → N14（pass）/ → N15（fail） | — |
| N14 | state.py: task_status → 待驗收（同步 tasks.md） | call | → S1, → S2 | — |
| N15 | state.py: task_list[current] → `[ ]`、task_status → 待實作、retry_count++、reviewer_notes（同步 tasks.md） | call | → S1, → S2 | — |

### P4 — Judge Loop

| # | Affordance | Control | Wires Out | Returns To |
|---|------------|---------|-----------|------------|
| N20 | 讀取 state.json | call | — | → N21 |
| N21 | system_status == running AND task_status == 待驗收? | conditional | → N22（yes）/ → N20（no，等下輪） | — |
| N22 | `git log -p -3` | call | — | → N23 |
| N23 | 驗收任務需求符合度 + 偏離偵測 | call | → N24（accept）/ → N25（reject） | — |
| N24 | state.py: task_list[current] → `[x]`、advance current_task_index、reset retry_count（同步 tasks.md） | call | → S1, → S2 | — |
| N25 | state.py: task_list[current] → `[ ]`、task_status → 待實作、retry_count++、judge_notes（同步 tasks.md） | call | → S1, → S2 | — |

---

## Diagram

```mermaid
flowchart TB
    subgraph P1["P1: User Terminal"]
        U1["U1: bash start.sh"]
        N1["N1: cp settings → .claude/"]
        N2["N2: 讀 tasks.md → task_list + [ ]"]
        N3i["N3_init: print startup commands"]
        U2["U2: 三段啟動指令"]
        U1 --> N1
        N1 --> N2
        N2 --> N3i
        N3i --> U2
    end

    subgraph P2["P2: Executor Loop"]
        U3["U3: executor.md"]
        N3["N3: 讀 state.json"]
        N4{"N4: 待實作?"}
        N5["N5: 實作 + git commit"]
        N6["N6: state.py: [/] + 待審查"]
        N8["N8: append implementation_done.md"]
        U3 --> N3
        N3 --> N4
        N4 -->|yes| N5
        N4 -->|no| N3
        N5 --> N6
        N6 --> N8
    end

    subgraph P3["P3: Reviewer Loop"]
        U4["U4: reviewer.md"]
        N10["N10: 讀 state.json"]
        N11{"N11: 待審查?"}
        N12["N12: git show HEAD"]
        N13["N13: 審查"]
        N14["N14: state.py: 待驗收"]
        N15["N15: state.py: [ ] + 待實作 + retry++"]
        U4 --> N10
        N10 --> N11
        N11 -->|yes| N12
        N11 -->|no| N10
        N12 --> N13
        N13 -->|pass| N14
        N13 -->|fail| N15
    end

    subgraph P4["P4: Judge Loop"]
        U5["U5: judge.md"]
        N20["N20: 讀 state.json"]
        N21{"N21: 待驗收?"}
        N22["N22: git log -p -3"]
        N23["N23: 驗收"]
        N24["N24: state.py: [x] + advance"]
        N25["N25: state.py: [ ] + 待實作 + retry++"]
        U5 --> N20
        N20 --> N21
        N21 -->|yes| N22
        N21 -->|no| N20
        N22 --> N23
        N23 -->|accept| N24
        N23 -->|reject| N25
    end

    S1[("S1: state.json")]
    S2[("S2: tasks.md\n← synced by state.py")]
    S3[("S3: .claude/settings.json")]
    S4[("S4: git history")]
    S5[("S5: implementation_done.md")]

    N1 --> S3
    N2 --> S1
    N5 --> S4
    N6 --> S1
    N6 --> S2
    N8 --> S5
    N12 -->|reads| S4
    N14 --> S1
    N14 --> S2
    N15 --> S1
    N15 --> S2
    N22 -->|reads| S4
    N24 --> S1
    N24 --> S2
    N25 --> S1
    N25 --> S2

    S1 -.-> N3
    S1 -.-> N10
    S1 -.-> N20

    classDef ui fill:#ffb6c1,stroke:#d87093,color:#000
    classDef code fill:#d3d3d3,stroke:#808080,color:#000
    classDef store fill:#e6e6fa,stroke:#9370db,color:#000
    classDef cond fill:#fffacd,stroke:#daa520,color:#000

    class U1,U2,U3,U4,U5 ui
    class N1,N2,N3i,N3,N5,N6,N8,N10,N12,N13,N14,N15,N20,N22,N23,N24,N25 code
    class N4,N11,N21 cond
    class S1,S2,S3,S4,S5 store
```

---

## v2 新增對照表

| 新增 Affordance | 對應 Shape part |
|----------------|----------------|
| N1, N2, N3_init, U2 | A1 — start.sh 改版（含 task_list 初始化） |
| U3/U4/U5 路徑改為 `workflow/agents/` | A2 — 目錄重整 |
| N12（`git show HEAD`） | A3 — Reviewer git 上下文 |
| N22（`git log -p -3`） | A3 — Judge git 上下文 |
| N6, N15, N24, N25（state.py 帶前綴 + 同步 tasks.md） | A4 — 任務標記（state.json 為 source of truth） |
| N8, S5 | A5 — 實作摘要紀錄 |
