"""Entry point for the Workflow Patterns MCP server."""

from workflow_patterns.mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run()
