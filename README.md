# ollama-mcp-server

[![CodeQL](https://github.com/AlexandreGuil/ollama-mcp-server/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/AlexandreGuil/ollama-mcp-server/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A minimal [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server
that bridges Claude Code (or any MCP-compatible client) to a **local
[Ollama](https://ollama.com)** instance.

The server exposes a single tool, `query_ollama`, that forwards a prompt to
`http://localhost:11434` and returns the response. **No data leaves the machine.**

---

## Why use this

- **Save cloud tokens.** Let Claude orchestrate the hard part and delegate the
  cheap, local-only steps (file summary, boilerplate, "explain this snippet")
  to a model running on your own hardware.
- **Keep prompts on-machine.** The server speaks only to `localhost:11434`.
- **Zero config.** The script is one self-contained file (~80 lines, PEP 723
  inline dependencies). No `pip install`, no virtualenv to manage by hand.

---

## Requirements

| Component      | Version       | Notes |
|----------------|---------------|-------|
| Python         | **3.10+**     | Needed only by `uv` to run the script |
| [`uv`](https://github.com/astral-sh/uv) | latest    | Resolves the inline `mcp` and `httpx` deps |
| [Ollama](https://ollama.com)            | 0.1.32+   | Must be reachable at `http://localhost:11434` |
| MCP client     | any           | Tested with [Claude Code](https://claude.com/claude-code) |
| At least one Ollama model pulled locally | — | Default: `qwen2.5-coder:14b` |

---

## Quick start (TL;DR)

```bash
# 1. Install Ollama and pull a model
brew install ollama          # macOS — see below for Linux/Windows
ollama serve &
ollama pull qwen2.5-coder:14b

# 2. Get the script
git clone https://github.com/AlexandreGuil/ollama-mcp-server.git
cd ollama-mcp-server

# 3. Register the server with Claude Code
claude mcp add -s user ollama-local -- "$(which uv)" run "$PWD/ollama_mcp_server.py"

# 4. Verify
claude mcp list
```

Then open Claude Code and ask:

> *"Use query_ollama to summarise this file in one sentence."*

If you see the local model respond, you are done.

---

## Full setup

### 1. Install Ollama and pull a model

| OS | Install command |
|----|-----------------|
| macOS | `brew install ollama` |
| Linux | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Windows / WSL2 | Download installer from [ollama.com/download](https://ollama.com/download) |

Then start the server (it runs as a daemon) and pull a model:

```bash
ollama serve &                  # or: launch the Ollama app on macOS
ollama pull qwen2.5-coder:14b   # ~9 GB, runs comfortably on 16 GB RAM
ollama list                     # verify the model is available
```

Other small-to-mid models worth trying: `llama3.2:3b` (~2 GB),
`qwen2.5:7b` (~4.5 GB), `gemma2:9b` (~5.5 GB).

### 2. Get the script

**Option A — git clone (recommended, easier to update):**

```bash
git clone https://github.com/AlexandreGuil/ollama-mcp-server.git
cd ollama-mcp-server
```

**Option B — single-file download (no git history kept):**

```bash
mkdir -p ~/bin
curl -fsSL https://raw.githubusercontent.com/AlexandreGuil/ollama-mcp-server/main/ollama_mcp_server.py \
  -o ~/bin/ollama_mcp_server.py
```

The script is fully self-contained, so it works from anywhere on disk.

### 3. Register the server with Claude Code

Claude Code supports three configuration scopes — pick the one you want:

| Scope | Flag | Stored in | When to use |
|-------|------|-----------|-------------|
| **user** | `-s user` | `~/.claude.json` | Available in every project (recommended) |
| **project** | `-s project` | `<repo>/.mcp.json` | Shared with collaborators on this repo |
| **local** | `-s local` (default) | `~/.claude.json` (per-project) | Only on this machine for this project |

The most common choice is `user` — once registered, the tool shows up in every
Claude Code session you open on this machine.

```bash
# If you cloned the repo:
claude mcp add -s user ollama-local -- "$(which uv)" run "$PWD/ollama_mcp_server.py"

# If you downloaded the script to ~/bin/:
claude mcp add -s user ollama-local -- "$(which uv)" run "$HOME/bin/ollama_mcp_server.py"
```

Confirm it is registered:

```bash
claude mcp list
# Expected line:
# ollama-local: /Users/.../uv run /Users/.../ollama_mcp_server.py  ✓ Connected
```

Restart Claude Code (close all sessions) so the new server is picked up.

### 4. First test

Open a Claude Code session in any project and ask:

> *"Use the `query_ollama` tool to write a one-sentence summary of this README."*

Claude will call the tool and return the local model's response. If the tool is
not invoked, see [Troubleshooting](#troubleshooting).

---

## Using it in Claude Code

### How to ask Claude to delegate

Two equally valid patterns:

1. **Explicit** — name the tool. Most reliable.

   > *"Use `query_ollama` to draft a docstring for the function in `utils.py`."*

2. **Hinted** — describe the intent and let Claude decide. Works once the
   assistant has learned (via CLAUDE.md, see below) that the tool exists.

   > *"Summarise this log file with the local model."*

Claude inserts a tool call to `query_ollama`, waits for the response, and folds
it back into the conversation. The prompt and the response never leave your
machine.

### Good fits for delegation

| ✅ Delegate | Why |
|------------|------|
| Summarising one file | Saves tokens, local model is competent enough |
| Drafting boilerplate (config, test stubs, README sections) | Cheap, repetitive |
| Explaining a snippet | Self-contained context |
| Rewriting text (FR↔EN, tone, polish) | No external context needed |
| Generating shell one-liners | Small ask, fast |
| Parsing a log / extracting structured info | Pattern matching |

### When **not** to delegate

| ❌ Keep on Claude | Why |
|------------------|------|
| Multi-file reasoning | Local models struggle to track cross-file context |
| Architecture decisions | You want top-tier judgement |
| Anything requiring internet, search, or external APIs | Local model has no tools |
| Production code where output quality is critical | The cost difference is worth it |

### Tip — encourage delegation in your `CLAUDE.md`

Drop a section like this into your project's `CLAUDE.md` so Claude reflexively
considers Ollama for tasks that fit:

```markdown
## Local MCP — query_ollama

An MCP tool `query_ollama` is registered (see ollama-mcp-server). Before doing
anything that matches the patterns below, consider delegating to it instead of
spending cloud tokens:

- reading and summarising a single file
- drafting boilerplate (test stubs, config, README sections)
- explaining a code snippet
- rewriting / translating text
- generating shell one-liners

Use your own capabilities for: multi-file reasoning, internet access, tool
orchestration, or anywhere output quality is critical.
```

---

## Configuration

The script intentionally has **no config file and no environment variables**.
If you need to change the endpoint, default model, or timeout, edit the three
constants at the top of `ollama_mcp_server.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL   = "qwen2.5-coder:14b"
REQUEST_TIMEOUT = 120.0
```

The MCP client can override `model` (and pass a `system` prompt) per call:

| Field    | Type   | Required | Default               |
|----------|--------|----------|-----------------------|
| `prompt` | string | yes      | —                     |
| `model`  | string | no       | `DEFAULT_MODEL`       |
| `system` | string | no       | _(none)_              |

The server calls `POST /api/generate` on Ollama (non-streaming) and returns the
`response` field as a single text block.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `connection refused` from the tool call | Ollama is not running | `ollama serve` (or launch the Ollama app) and confirm `curl http://localhost:11434/api/tags` returns JSON |
| `model "<name>" not found` | Model not pulled | `ollama pull <name>` then retry |
| `claude mcp list` does not show `ollama-local` | Not registered, or registered in wrong scope | Re-run the `claude mcp add` command from step 3 |
| `ollama-local: ✗ Failed to connect` in `claude mcp list` | Path to `uv` or to the script is wrong | Re-run `claude mcp add` with absolute paths, or check `which uv` |
| Tool call hangs for >120s | Model is large, hardware slow, or first cold-start of model | Increase `REQUEST_TIMEOUT` in the script, or switch to a smaller model |
| Claude does not invoke the tool even when asked | Server registered but session started before — Claude Code caches the tool list | Restart Claude Code |
| Tool returns empty text | Ollama returned no `response` field (rare; usually a model load error) | Check Ollama logs (`journalctl -u ollama` on Linux, Console.app on macOS) |

---

## Security notes

- The server talks **only to `localhost`** — no outbound network traffic.
- It is started as a **stdio** MCP child process by Claude Code; it does not
  listen on any port itself.
- Prompts passed to the tool are sent to your local Ollama instance verbatim.
  If your prompts contain secrets, they end up in Ollama's logs (and possibly
  in the model's context window if you have telemetry enabled in Ollama). Use
  judgement.
- This project is provided **AS IS**, with no warranty. See [LICENSE](LICENSE).
- To report a vulnerability privately, see [SECURITY.md](SECURITY.md).

---

## Development

Want to tweak the server? The script has no test harness — it's intentionally
small enough to read in one sitting. To try a change:

1. Edit `ollama_mcp_server.py`.
2. Restart Claude Code so it re-spawns the MCP child process.
3. Exercise the tool from a session.

Contributions are welcome via pull request. Branch protection requires that the
[CodeQL](.github/workflows/codeql.yml) check passes on `main`, so make sure your
PR is green before requesting review.

---

## License

[MIT](LICENSE) © 2026 Alexandre Guillemot
