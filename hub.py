"""The 'MCP of MCPs'. The LLM host connects ONLY to this server, over HTTP.

Auth flow:
    MCP host --Authorization: Bearer <user JWT>--> hub --same header--> every backend
The hub checks the JWT once at the door, then its proxies copy the caller's
Authorization header onto each backend request, so every backend sees the real user.
Per-backend fixed headers (API keys etc.) come from backends.json and are sent too.

Backends are listed in backends.json (same format as claude_desktop_config.json).
${VAR} placeholders are filled from the environment / .env.

    HUB_MODE=flat    -> LLM sees every backend tool, prefixed office_* / retriever_*
    HUB_MODE=search  -> LLM sees 2 tools: search_tools + call_tool (default)
"""
import json
import os
from pathlib import Path

os.environ.setdefault("FASTMCP_LOG_LEVEL", "WARNING")  # quiet startup logs

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server import create_proxy
from fastmcp.server.transforms.search import BM25SearchTransform

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

from jwt_config import verifier  # noqa: E402  (reads JWT_* from .env)

config_text = (HERE / os.getenv("HUB_BACKENDS", "backends.json")).read_text()
BACKENDS = json.loads(os.path.expandvars(config_text))["mcpServers"]

# auth=... rejects bad/missing JWTs at the hub (401) before any backend is contacted.
hub = FastMCP("hub", auth=verifier())

for namespace, cfg in BACKENDS.items():
    # Proxies forward the incoming Authorization header (the user's JWT) upstream.
    backend = create_proxy({"mcpServers": {namespace: cfg}}, name=namespace)
    hub.mount(backend, namespace=namespace)

if os.getenv("HUB_MODE", "search") == "search":
    hub.add_transform(BM25SearchTransform(max_results=3))

if __name__ == "__main__":
    # Must be HTTP: stdio has no headers, so there would be no JWT to forward.
    hub.run(transport="http", host="127.0.0.1", port=int(os.getenv("HUB_PORT", "8000")),
            show_banner=False)
