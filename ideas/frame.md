---
shaping: true
---

# Claude Code 多角色工作流 — Frame

## Source

### 作者（transcript.md）

> 「我目前建立了使用 sbx 開啟獨立環境的方法，接著我想要設計 claude code 的工作流。」

> 「會有三個角色：Excuter, Reviewer, Judge」

> 「會有一個存放目前進度的文件，此文件可以讓三個角色輪流工作」

> 「三個角色會是獨立的 context window，他們會跑 loop 並等待自己的任務」

> 「三個角色會一直工作直到任務列表被消化完」

狀態機流程（逐字引用）：

> 「當前任務有以下情境：
> 1. 可以開始實作 → Excuter 工作
> 2. 可以開始 Review → Reviewer 工作
> 3. 如果需要改寫 → 回到 1 退還給 Excuter 工作
> 4. 如果 Review 完畢，不需要改 → 給 Judge 判定是否有符合當前任務需求
> 5. 如果 Judge 判定不符合需求 → 回到 1
> 6. 如果 Judge 判定符合需求 → 進行下一個任務」

---

## Pre-work：工作流選項景觀

Transcript 只提出一個明確的方向。沒有其他選項浮現並獲得討論，因此這裡不虛構競爭方案。

| 選項 | 內容 | 誰受益 | 訊號強度 |
|------|------|--------|----------|
| **A. 三角色流水線（Executor / Reviewer / Judge）** | 每個角色獨立 context window，共享進度文件，狀態機驅動任務流轉 | 需要在 sbx 環境中自動完成多步驟任務的使用者 | 唯一提出的方向，細節描述完整 |

**為什麼是 A：** 這是 transcript 中唯一一個具體到可以開始設計的方向。它直接建立在已完成的基礎設施（sbx 獨立環境）上，並解決一個具體的操作問題——單一 context window 無法同時承擔實作、審查與驗收三種不同性質的工作。

---

## Problem

- 單一 Claude Code session 的 context window 必須同時承擔實作、審查、驗收，角色混用（可從 transcript 的三角色設計直接反推）
- 沒有強制的品質閘門：實作完成後是否符合任務需求，沒有獨立機制確認
- 沒有狀態持久化：工作進度與任務列表依賴 session 內記憶，無法跨 context 接續

## Outcome

- 三個獨立 context window 各司其職，互不污染
- 任務進度持久化在共享文件中，任何角色都可以從文件中取得當前狀態
- 工作流可以在無人介入的情況下，自動從頭執行到整份任務列表消化完畢

---

## Less about

- 讓單一 Claude session 變得更聰明或更有記憶
- 加速個別任務的執行速度

## More about

- 用角色分工與狀態機取代單一 session 的萬能假設
- 讓品質控制（Review、Judge）成為流程的一等公民，而不是事後補丁
