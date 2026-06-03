#!/usr/bin/env python3
"""
MCP Server v11 Unified - Stdio Entry Point
Same server as mcp_http_server.py but runs via stdio transport.
Used by OpenCode, Gemini CLI, and other stdio-based MCP clients.
"""
import sys
from pathlib import Path

# Setup paths
current_dir = Path(__file__).resolve().parent
mcp_hub_root = current_dir.parent
sys.path.insert(0, str(mcp_hub_root))
sys.path.insert(0, str(current_dir))

from mcp_http_server import mcp

if __name__ == "__main__":
    mcp.run()
