#!/usr/bin/env python3
"""
MCP Server v11 Unified - Stdio Entry Point
Same server as mcp_http_server.py but runs via stdio transport.
Used by OpenCode, Gemini CLI, and other stdio-based MCP clients.
"""
import sys
import os
import traceback
from pathlib import Path

# --- MCP stdio protection (issue #225) -----------------------------------
# Redirect stdout → stderr at both the Python and file-descriptor level 
# before heavy imports, then restore the real stdout in main() before 
# entering the protocol loop. This prevents onnxruntime/chromadb C-level 
# prints from breaking the JSON-RPC stdout pipe.
_REAL_STDOUT = sys.stdout
_REAL_STDOUT_FD = None
try:
    _REAL_STDOUT_FD = os.dup(1)
    os.dup2(2, 1)
except (OSError, AttributeError):
    pass
sys.stdout = sys.stderr

# Setup simple debug log
# Derive the log path from the script location so this works from any clone
# (was hardcoded to the original developer's workspace, which broke on every
# other machine). Logs now land at <repoRoot>/logs/stdio_debug.log.
log_file = Path(__file__).resolve().parent.parent / "logs" / "stdio_debug.log"
log_file.parent.mkdir(parents=True, exist_ok=True)
def dlog(msg):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

dlog("--- mcp_stdio.py started (with stdout protection) ---")

try:
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
        # Restore real stdout for MCP JSON-RPC output
        if _REAL_STDOUT_FD is not None:
            try:
                os.dup2(_REAL_STDOUT_FD, 1)
                os.close(_REAL_STDOUT_FD)
            except OSError:
                pass
            _REAL_STDOUT_FD = None
        sys.stdout = _REAL_STDOUT

        dlog("Starting mcp.run(transport='stdio')...")
        mcp.run(transport='stdio')
        dlog("mcp.run finished cleanly.")
except Exception as e:
    dlog(f"ERROR: {e}\n{traceback.format_exc()}")


