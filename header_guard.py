"""Tiny ASGI middleware: reject any HTTP request missing the required header (-> 401).
Stands in for whatever auth your real remote MCP servers enforce."""
from starlette.middleware import Middleware
from starlette.responses import JSONResponse


class _HeaderGuard:
    def __init__(self, app, header: str, value: str):
        self.app, self.header, self.value = app, header.lower().encode(), value.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and dict(scope["headers"]).get(self.header) != self.value:
            return await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)
        await self.app(scope, receive, send)


def require_header(header: str, value: str) -> list[Middleware]:
    return [Middleware(_HeaderGuard, header=header, value=value)]
