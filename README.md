# Three little Ralphs

![](Image_7vpqd47vpqd47vpq.png)

A sandbox for experimenting with multi-agent Claude Code workflows running inside Docker Sandboxes (`sbx`). The `workflow/` directory orchestrates three specialized agents (Executor, Reviewer, Judge) running in parallel ralph loops.

---

## Setup: Docker AI Sandbox (sbx)

Docker Sandboxes run AI coding agents in isolated **microVMs** with their own filesystem and network.

### Install

**macOS:**
```bash
brew install docker/tap/sbx
sbx login
```

**Windows:**
```bash
winget install -h Docker.sbx
sbx login
```

**Linux (Ubuntu):**
```bash
curl -fsSL https://get.docker.com | sudo REPO_ONLY=1 sh
sudo apt-get install docker-sbx
sudo usermod -aG kvm $USER
newgrp kvm
sbx login
```

### Common Commands

| Command | Description |
|---------|-------------|
| `sbx run claude` | Start Claude Code inside sandbox |
| `sbx ls` | List all sandboxes |
| `sbx stop <name>` | Pause sandbox |
| `sbx rm <name>` | Delete sandbox |
| `sbx exec -it <name> bash` | Open shell inside sandbox |

### Branch Mode (for multi-agent runs)

```bash
sbx run --branch auto claude
```

Each agent gets its own git worktree under `.sbx/`, avoiding conflicts when running in parallel.

### Port Forwarding

- Services inside sandbox must bind to `0.0.0.0`
- Access host services via `host.docker.internal`

---

## Running the Multi-Agent Workflow

### First Time (new project)

Copy `workflow/` into the target project root.

### Each Run

**1. Define tasks** — edit `workflow/tasks.md`, one task per `- ` bullet:

```markdown
- 實作登入 API，接受帳號密碼，回傳 JWT token
- 實作登出 API，清除 session
```

**2. Initialize state:**

```bash
bash workflow/start.sh
```

**3. Launch agents** — open four terminals:

```bash
# Terminal 1 — Monitor / manual queries
cd test-todo-project && sbx run claude

# Terminal 2 — Judge (start first)
sbx run claude
# then type: /loop 1min 執行 workflow/agents/judge.md 的工作

# Terminal 3 — Reviewer
sbx run claude
# then type: /loop 1min 執行 workflow/agents/reviewer.md 的工作

# Terminal 4 — Executor (start last)
sbx run claude
# then type: /loop 1min 執行 workflow/agents/executor.md 的工作
```

**4. Monitor state:**

```bash
python3 workflow/state.py read
```

### Resuming After Pause

When `system_status` becomes `waiting_for_user` (after 3 retries or detected deviation), all agents stop. Check `reviewer_notes` / `judge_notes`:

```bash
python3 workflow/state.py read
```

Resume:

```bash
python3 workflow/state.py write '{"system_status": "running"}'
```

---

## Workflow Architecture

State is managed in `workflow/state.json`. Agents coordinate exclusively through this file — no direct communication.

**State fields:**

| Field | Values |
|-------|--------|
| `system_status` | `running` \| `waiting_for_user` \| `done` |
| `task_status` | `待實作` \| `待審查` \| `待驗收` \| `完成` |
| `current_task_index` | index into `task_list` |
| `retry_count` | increments on reject; pauses at ≥ 3 |
| `reviewer_notes` / `judge_notes` | rejection reasons |

**Agent responsibilities:**

- **Executor** — acts on `待實作`: implements code, commits, advances to `待審查`
- **Reviewer** — acts on `待審查`: reviews code quality; passes to `待驗收` or rejects back
- **Judge** — acts on `待驗收`: checks for deviation; accepts and advances or rejects

---

## Agent Settings

`settings/agent-claude-settings.json` is the locked-down permission profile for agents inside `sbx`. Blocks: `.env` reads/writes, `rm -rf`, `sudo`, `git push`, writes to `*.production.*` / `*.prod.*`.

```bash
cp workflow/settings/agent-claude-settings.json .claude/settings.json
sbx run claude
```
