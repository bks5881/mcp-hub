"""Backend #2: a pretend 'Golden Retriever' (document retrieval / RAG) server with 4 tools."""
import os
os.environ.setdefault("FASTMCP_LOG_LEVEL", "WARNING")  # quiet startup logs

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from header_guard import require_header
from jwt_config import verifier

mcp = FastMCP("golden_retriever", auth=verifier())  # rejects requests without a valid JWT

DOCS = {
    "gdpr-art-17": "Right to erasure ('right to be forgotten') ...",
    "greek-civil-code-914": "Whoever unlawfully and culpably causes damage to another ...",
}

@mcp.tool
def search_knowledge_base(query: str, top_k: int = 3) -> list[str]:
    """Semantic search over the legal knowledge base; returns matching document ids."""
    return [d for d in DOCS if any(w in DOCS[d].lower() for w in query.lower().split())][:top_k] or list(DOCS)[:top_k]

@mcp.tool
def fetch_document(doc_id: str) -> str:
    """Fetch the full text of a knowledge-base document by id."""
    user = get_access_token().claims["sub"]
    return f"{DOCS.get(doc_id, 'not found')} (fetched for {user})"

@mcp.tool
def index_document(doc_id: str, text: str) -> str:
    """Add or update a document in the knowledge base index."""
    DOCS[doc_id] = text
    return f"Indexed {doc_id}"

@mcp.tool
def summarize_document(doc_id: str) -> str:
    """Return a short summary of a knowledge-base document."""
    return DOCS.get(doc_id, "not found")[:40] + "..."

if __name__ == "__main__":
    # Streamable-HTTP server at http://127.0.0.1:8002/mcp. Needs BOTH the user's
    # `Authorization: Bearer <JWT>` AND a fixed `X-API-Key` that only the hub knows.
    mcp.run(transport="http", host="127.0.0.1", port=8002, show_banner=False,
            middleware=require_header("X-API-Key", "retriever-secret"))
