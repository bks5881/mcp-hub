#!/bin/sh
# Start the two demo backends as HTTP servers (stand-ins for your remote/local HTTP MCPs).
cd "$(dirname "$0")"
uv run python office_server.py & uv run python golden_retriever_server.py & wait
