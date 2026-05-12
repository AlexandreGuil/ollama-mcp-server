# ollama-mcp-server

A minimal [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server
that bridges Claude Code (and other MCP-compatible clients) to a **local
[Ollama](https://ollama.com)** instance.

The server exposes a single tool, `query_ollama`, that forwards a prompt to
`http://localhost:11434` and returns the response. **No data leaves the machine.**

Useful when you want Claude Code to offload local-only tasks (summarising a
file, drafting boilerplate, simple code review) to a model running on your own
hardware instead of consuming cloud tokens.

---

## Requirements

- Python **3.10+**
- [`uv`](https://github.com/astral-sh/uv) (the script uses PEP 723 inline dependencies)
- A running Ollama server reachable at `http://localhost:11434`
- At least one model pulled locally (default: `qwen2.5-coder:14b`)

```bash
# Ollama install (macOS)
brew install ollama
ollama serve &
ollama pull qwen2.5-coder:14b
```

---

## Install

```bash
git clone https://github.com/AlexandreGuil/ollama-mcp-server.git
cd ollama-mcp-server
```

Register the server with Claude Code (user scope):

```bash
claude mcp add -s user ollama-local -- \
  $(which uv) run "$PWD/ollama_mcp_server.py"
```

You can also keep the script anywhere on disk (e.g. `~/bin/`) and point the
`claude mcp add` command to that path — the script is fully self-contained.

---

## Usage

Once registered, the tool `query_ollama` becomes available in any Claude Code
session. The MCP client passes:

| Field    | Type   | Required | Default               |
|----------|--------|----------|-----------------------|
| `prompt` | string | yes      | —                     |
| `model`  | string | no       | `qwen2.5-coder:14b`   |
| `system` | string | no       | _(none)_              |

Example invocation (from inside Claude Code, by the assistant):

```json
{
  "name": "query_ollama",
  "arguments": {
    "prompt": "Summarise this Python function in one sentence: ...",
    "model": "qwen2.5-coder:14b"
  }
}
```

The server posts to `POST /api/generate` on Ollama (non-streaming) and returns
the `response` field as a single text block.

---

## Configuration

The script intentionally has **no config file and no environment variables**.
If you need to change the endpoint or default model, edit the three constants
at the top of `ollama_mcp_server.py`:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL   = "qwen2.5-coder:14b"
REQUEST_TIMEOUT = 120.0
```

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

## License

[MIT](LICENSE) © 2026 Alexandre Guillemot
