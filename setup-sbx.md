# 啟用 Docker AI Sandbox (sbx)

Docker Sandboxes 把 AI coding agent 跑在獨立的 **microVM** 裡，每個 sandbox 有自己的 Docker daemon、filesystem 和 network，與 host 完全隔離。

官方文件：https://docs.docker.com/ai/sandboxes/usage/

---

## 前置需求

- macOS、Windows 或 Linux（Ubuntu）
- Docker CLI 或 Docker Desktop 已安裝
- Linux 額外需要：KVM 支援 + sudo 權限

---

## 安裝 sbx CLI

**macOS：**
```bash
brew install docker/tap/sbx
sbx login
```

**Windows：**
```bash
winget install -h Docker.sbx
sbx login
```

**Linux（Ubuntu）：**
```bash
curl -fsSL https://get.docker.com | sudo REPO_ONLY=1 sh
sudo apt-get install docker-sbx
sudo usermod -aG kvm $USER
newgrp kvm
sbx login
```

---

## 快速啟動

```bash
cd ~/my-project
sbx run claude
```

進入專案目錄後執行，會在 sandbox microVM 內啟動 Claude Code。

---

## 常用指令

| 指令 | 說明 |
|------|------|
| `sbx run claude` | 在 sandbox 內啟動 Claude Code |
| `sbx ls` | 列出所有 sandbox 及狀態 |
| `sbx stop <name>` | 暫停 sandbox |
| `sbx rm <name>` | 刪除 sandbox |
| `sbx exec -it <name> bash` | 進入 sandbox 的 shell |
| `sbx ports` | 設定 port forwarding |
| `sbx`（無參數） | 開啟互動式 dashboard |

---

## Git 整合模式

**Direct mode（預設）：** agent 直接修改 working tree，變更立即反映到 host。

**Branch mode：** 每個 agent 有自己的 git worktree，避免多個 agent 同時跑時衝突：

```bash
sbx run --branch auto claude        # 自動命名 branch
sbx run --branch my-feature claude  # 指定 branch 名稱
```

worktree 會建在 `.sbx/` 目錄下，從最新 commit 分支出去（未 commit 的變更不會帶入）。

---

## 其他實用選項

**掛載額外目錄：**
```bash
sbx run --mount /other/dir claude
sbx run --mount /read-only/dir:ro claude  # 唯讀
```

**指定 sandbox 名稱：**
```bash
sbx run --name my-sandbox claude
```

**Port forwarding：**
- agent 內的服務需 bind 到 `0.0.0.0`（不能用 `127.0.0.1`）
- 存取 host 的服務用 `host.docker.internal`

---

## 隔離範圍

| 項目 | 隔離狀況 |
|------|----------|
| Filesystem | ✅ microVM 內，專案目錄 mount 進去 |
| Docker daemon | ✅ 獨立 daemon，`docker ps` 在 host 看不到 |
| Network | ✅ private network，可設定 governance 規則 |
| Packages 安裝 | agent 有 sudo，安裝結果在 sandbox 生命週期內持續存在 |
| Sandbox 移除後 | 只有 workspace 檔案留在 host，其餘清空 |

---

## 與 Debian VM 方式的比較

| | Docker Sandbox (sbx) | Debian VM (OrbStack) |
|---|---|---|
| 底層技術 | microVM | Full VM |
| 啟動速度 | 快 | 較慢（需開機） |
| 隔離強度 | microVM 層級（含獨立 Docker daemon） | 完整 OS 層級 |
| 設定複雜度 | 低（一個指令） | 中（見 `setup-vm`） |
| Git 整合 | 內建 branch mode | 手動處理 |
| 適合場景 | 快速迭代、多 agent 並行 | 需要完整 OS 控制的場景 |
