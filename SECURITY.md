# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability in `ollama-mcp-server`,
**please do not open a public GitHub issue**.

Instead, report it privately via GitHub's built-in private vulnerability
reporting:

1. Go to the [Security tab](https://github.com/AlexandreGuil/ollama-mcp-server/security)
   of this repository.
2. Click **Report a vulnerability**.
3. Fill in the form with as much detail as you can (reproduction steps,
   affected version, impact assessment).

I will acknowledge your report within **7 days** and aim to provide an initial
assessment within **14 days**.

## Scope

This project is a thin (~80 lines) MCP bridge to a **local** Ollama instance.
Its attack surface is intentionally minimal:

- It speaks the MCP stdio protocol with its parent process (Claude Code or
  another MCP client).
- It makes HTTP POST calls to `http://localhost:11434` only.
- It does not read or write any file on disk.
- It does not handle credentials.

In-scope issues include, but are not limited to:

- Ways to make the server perform unintended network calls outside of
  `localhost`.
- Ways to make the server execute arbitrary code on the host.
- Vulnerabilities in the inline dependency manifest that could lead to a
  supply-chain compromise.

Out-of-scope:

- Vulnerabilities in **Ollama itself** — please report those to the upstream
  Ollama project.
- Vulnerabilities in the MCP SDK (`mcp` Python package) — please report those
  to the upstream MCP project.
- "The server forwards my prompt to a local LLM that may hallucinate" — this
  is expected behaviour, not a vulnerability.

## Supported versions

The repository ships a single script. Only the **latest commit on `main`** is
supported. There are no LTS branches.

## Disclosure

Once a fix is shipped, I will publish a GitHub Security Advisory crediting the
reporter (unless you prefer to remain anonymous).
