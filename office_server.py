"""Backend #1: a pretend 'Office' MCP server with 5 tools."""
import os
os.environ.setdefault("FASTMCP_LOG_LEVEL", "WARNING")  # quiet startup logs

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from jwt_config import verifier

mcp = FastMCP("office", auth=verifier())  # rejects requests without a valid JWT

@mcp.tool
def create_document(title: str, body: str) -> str:
    """Create a new Word-style document with a title and body text."""
    return f"Created document '{title}' ({len(body)} chars)"

@mcp.tool
def read_spreadsheet(filename: str, sheet: str = "Sheet1") -> list[list[str]]:
    """Read rows from an Excel spreadsheet."""
    return [["Name", "Q3 Revenue"], ["Acme", "120000"], ["Globex", "98000"]]

@mcp.tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Outlook."""
    user = get_access_token().claims["sub"]
    return f"Email to {to} with subject '{subject}' queued (sent as {user})"

@mcp.tool
def schedule_meeting(attendees: list[str], when: str, topic: str) -> str:
    """Schedule a calendar meeting with attendees."""
    return f"Meeting '{topic}' at {when} with {', '.join(attendees)}"

@mcp.tool
def make_slides(topic: str, num_slides: int = 5) -> str:
    """Generate a PowerPoint slide deck about a topic."""
    return f"Deck on '{topic}' with {num_slides} slides"

if __name__ == "__main__":
    # Streamable-HTTP server at http://127.0.0.1:8001/mcp; needs `Authorization: Bearer <JWT>`
    mcp.run(transport="http", host="127.0.0.1", port=8001, show_banner=False)
