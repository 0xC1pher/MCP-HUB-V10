#!/usr/bin/env python3
"""
MCP Server v11 Unified - Stdio Entry Point
Same server as mcp_http_server.py but runs via stdio transport.
Used by OpenCode, Gemini CLI, and other stdio-based MCP clients.
"""
import sys
import os
from pathlib import Path

# Disable Visual Activity Monitor for stdio mode (it pollutes stdout)
os.environ["MCP_DISABLE_VISUAL_MONITOR"] = "1"

# Setup paths
current_dir = Path(__file__).resolve().parent
mcp_hub_root = current_dir.parent
sys.path.insert(0, str(mcp_hub_root))
sys.path.insert(0, str(current_dir))

# Patch visual_monitor before import to prevent startup
import types
_fake_vm = types.ModuleType("visual_monitor")
_fake_vm.get_visual_monitor = lambda: None
_fake_vm.VisualActivityMonitor = type("VisualActivityMonitor", (), {})
sys.modules["visual_monitor"] = _fake_vm

from mcp_http_server import mcp

if __name__ == "__main__":
    # Force stdio transport regardless of whether running in a TTY or not
    mcp.run(transport='stdio')
