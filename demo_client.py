"""Acts like the MCP host: connects ONLY to the hub over HTTP with a user's JWT.

Start the backends (./run_backends.sh) and the hub (uv run python hub.py) first.
"""
import asyncio
import os

from fastmcp import Client

from jwt_config import mint_demo_token

HUB_URL = os.getenv("HUB_URL", "http://127.0.0.1:8000/mcp")


async def session(user: str, token: str):
    async with Client(HUB_URL, auth=token) as c:  # sends Authorization: Bearer <token>
        names = [t.name for t in await c.list_tools()]
        print(f"[{user}] tools the LLM sees: {names}")
        via = (lambda n, a: c.call_tool("call_tool", {"name": n, "arguments": a})) \
            if "call_tool" in names else c.call_tool
        r1 = await via("office_send_email", {"to": "boss@firm.gr", "subject": "hi", "body": "..."})
        r2 = await via("retriever_fetch_document", {"doc_id": "greek-civil-code-914"})
        print(f"[{user}] office    -> {r1.content[0].text}")
        print(f"[{user}] retriever -> {r2.content[0].text}")


async def main():
    # Two users at the same time: each backend must see the right user, never the other one.
    await asyncio.gather(session("alice", mint_demo_token("alice")),
                         session("bob", mint_demo_token("bob")))
    # No / bogus token must be rejected at the hub.
    for label, tok in [("no token", None), ("forged token", "eyJhbGciOiJub25lIn0.e30.")]:
        try:
            async with Client(HUB_URL, auth=tok) as c:
                await c.list_tools()
            print(f"[{label}] UNEXPECTEDLY ALLOWED")
        except Exception as e:
            print(f"[{label}] rejected: {type(e).__name__}")


asyncio.run(main())
