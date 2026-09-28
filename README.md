# mcp-hub
This is a example app of mcp orchestration of mcp of mcp

## Setup
    cp .env.example .env
    uv sync                      # installs dependencies (needs https://docs.astral.sh/uv/)

## Run (three terminals)
    ./run_backends.sh            # demo backends: office :8001, retriever :8002
    uv run python hub.py         # the hub at http://127.0.0.1:8000/mcp
    uv run python demo_client.py # connects to the hub with test JWTs

HUB_MODE=flat shows every tool; the default (search) shows only search_tools + call_tool.
Edit backends.json (and .env) to point the hub at your real MCP servers.
