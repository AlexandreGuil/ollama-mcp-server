#!/usr/bin/env python3
# /// script
# dependencies = ["mcp>=1.0.0", "httpx>=0.27.0"]
# ///
"""
MCP server bridging Claude Code to a local Ollama instance.
All data stays on-machine — zero network traffic.

Usage:
  uv run ~/bin/ollama_mcp_server.py

Registered via:
  claude mcp add -s user ollama-local -- $(which uv) run ~/bin/ollama_mcp_server.py
"""

import asyncio
import httpx
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:14b"
REQUEST_TIMEOUT = 120.0

server = Server("ollama-local")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_ollama",
            description=(
                "Delegate a task to the local Ollama model (qwen2.5-coder:14b). "
                "Use this for code analysis, refactoring suggestions, boilerplate generation, "
                "documentation drafting, or any task that does not require internet access. "
                "All processing happens locally — no data leaves the machine."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "model": {"type": "string", "default": DEFAULT_MODEL},
                    "system": {"type": "string"},
                },
                "required": ["prompt"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "query_ollama":
        raise ValueError(f"Unknown tool: {name}")
    payload = {
        "model": arguments.get("model", DEFAULT_MODEL),
        "prompt": arguments["prompt"],
        "stream": False,
    }
    if "system" in arguments:
        payload["system"] = arguments["system"]
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        r.raise_for_status()
    return [types.TextContent(type="text", text=r.json().get("response", "").strip())]


async def main():
    async with mcp.server.stdio.stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
