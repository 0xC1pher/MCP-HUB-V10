#!/usr/bin/env python3
"""
MCP Memory Gateway & Context Builder
====================================
Orchestrates and centralizes contexts, decisions, and knowledge across 
OpenCode, Gemini CLI, and claw-code using MemPalace.
"""

import os
import sys
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path

# Setup logging to stderr
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
logger = logging.getLogger("mcp_memory_gateway")

# Ensure Python can find mempalace
sys.path.insert(0, "C:/Python314/Lib/site-packages")

try:
    import mempalace
    from mempalace.mcp_server import (
        tool_add_drawer,
        tool_list_drawers,
        tool_search,
        tool_delete_drawer,
    )
    logger.info("mempalace module successfully imported")
except ImportError as e:
    logger.error(f"Failed to import mempalace: {e}")
    sys.exit(1)

# Path to store gateway-specific state (like current active feature)
STATE_FILE = Path.home() / ".mempalace" / "gateway_state.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_PROJECT = "motodiario"

def load_state():
    if STATE_FILE.is_file():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"active_feature": "global", "project": DEFAULT_PROJECT}

def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")

# ==================== CORE GATEWAY TOOLS ====================

def tool_status():
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    
    # Get counts for different rooms (layers)
    layers = ["context", "decisions", "knowledge", "tasks", "summaries"]
    counts = {}
    for layer in layers:
        res = tool_list_drawers(wing=project, room=layer, limit=1)
        # res looks like {"drawers": [...], "count": N, ...} or {"error": ...}
        if "drawers" in res:
            # Get total count (pagination count helper isn't always total, but we can list with high limit)
            all_res = tool_list_drawers(wing=project, room=layer, limit=100)
            counts[layer] = len(all_res.get("drawers", []))
        else:
            counts[layer] = 0
            
    return {
        "status": "online",
        "project": project,
        "active_feature": state.get("active_feature", "global"),
        "layers_summary": counts
    }

def tool_set_active_feature(feature_name: str, project_name: str = None):
    state = load_state()
    state["active_feature"] = feature_name
    if project_name:
        state["project"] = project_name
    save_state(state)
    return {
        "success": True,
        "active_feature": state["active_feature"],
        "project": state["project"]
    }

def tool_add_adr(title: str, reason: str, status: str = "accepted"):
    """Files an Architecture Decision Record (ADR)."""
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    
    # Generate sequential ID by checking existing decisions
    existing = tool_list_drawers(wing=project, room="decisions", limit=100)
    drawers = existing.get("drawers", [])
    next_num = len(drawers) + 1
    adr_id = f"ADR-{next_num:03d}"
    
    adr_content = {
        "id": adr_id,
        "title": title,
        "reason": reason,
        "status": status,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    content_str = json.dumps(adr_content, indent=2)
    res = tool_add_drawer(
        wing=project,
        room="decisions",
        content=content_str,
        added_by="memory_gateway"
    )
    
    if res.get("success"):
        return {"success": True, "adr_id": adr_id, "title": title}
    return {"success": False, "error": res.get("error", "Unknown error")}

def tool_add_knowledge(title: str, description: str, category: str = "general"):
    """Files stable project knowledge."""
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    
    k_content = {
        "title": title,
        "description": description,
        "category": category,
        "updated_at": datetime.now().isoformat()
    }
    
    res = tool_add_drawer(
        wing=project,
        room="knowledge",
        content=json.dumps(k_content, indent=2),
        added_by="memory_gateway"
    )
    return res

def tool_add_task(task_description: str, status: str = "in_progress"):
    """Files or updates task state."""
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    
    task_content = {
        "description": task_description,
        "status": status,
        "updated_at": datetime.now().isoformat()
    }
    
    # We use a deterministic ID based on description to allow upserting/updating tasks
    res = tool_add_drawer(
        wing=project,
        room="tasks",
        content=json.dumps(task_content, indent=2),
        added_by="memory_gateway"
    )
    return res

def tool_compress_session(summary: str, files_modified: list = None):
    """Files incremental summary of completed task/session."""
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    feature = state.get("active_feature", "global")
    
    sum_content = {
        "feature": feature,
        "summary": summary,
        "files": files_modified or [],
        "timestamp": datetime.now().isoformat()
    }
    
    res = tool_add_drawer(
        wing=project,
        room="summaries",
        content=json.dumps(sum_content, indent=2),
        added_by="memory_gateway"
    )
    return res

def tool_build_context(query: str = None):
    """
    Context Builder: Compiles an optimized, highly token-efficient context prompt
    containing relevant ADRs, active tasks, stable knowledge, and feature status.
    """
    state = load_state()
    project = state.get("project", DEFAULT_PROJECT)
    feature = state.get("active_feature", "global")
    
    context_blocks = []
    context_blocks.append(f"=== ACTIVE DEVELOPMENT CONTEXT ===")
    context_blocks.append(f"Project: {project}")
    context_blocks.append(f"Active Feature/Scope: {feature}")
    context_blocks.append(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Fetch ADRs (Decisions)
    decisions_res = tool_list_drawers(wing=project, room="decisions", limit=50)
    decisions = decisions_res.get("drawers", [])
    if decisions:
        context_blocks.append("\n--- ARCHITECTURAL DECISIONS (ADRs) ---")
        for d in decisions:
            # Get full content
            full_res = mempalace.mcp_server.tool_get_drawer(d["drawer_id"])
            if "content" in full_res:
                try:
                    adr = json.loads(full_res["content"])
                    context_blocks.append(f"- [{adr['id']}] {adr['title']}: {adr['reason']} ({adr['status']})")
                except Exception:
                    context_blocks.append(f"- {full_res['content']}")
                    
    # 2. Fetch Active Tasks
    tasks_res = tool_list_drawers(wing=project, room="tasks", limit=20)
    tasks = tasks_res.get("drawers", [])
    if tasks:
        context_blocks.append("\n--- ACTIVE TASKS ---")
        for t in tasks:
            full_res = mempalace.mcp_server.tool_get_drawer(t["drawer_id"])
            if "content" in full_res:
                try:
                    tk = json.loads(full_res["content"])
                    context_blocks.append(f"- {tk['description']} | Status: {tk['status']}")
                except Exception:
                    context_blocks.append(f"- {full_res['content']}")

    # 3. Fetch Semantic Knowledge matching query
    if query:
        search_res = tool_search(query=query, wing=project, room="knowledge", limit=3)
        matches = search_res.get("matches", [])
        if matches:
            context_blocks.append("\n--- RELEVANT KNOWLEDGE ---")
            for m in matches:
                # Get full text
                full_res = mempalace.mcp_server.tool_get_drawer(m["id"])
                if "content" in full_res:
                    try:
                        k = json.loads(full_res["content"])
                        context_blocks.append(f"* {k['title']}: {k['description']}")
                    except Exception:
                        context_blocks.append(f"* {full_res['content']}")

    # 4. Fetch Recent Summaries
    summaries_res = tool_list_drawers(wing=project, room="summaries", limit=3)
    summaries = summaries_res.get("drawers", [])
    if summaries:
        context_blocks.append("\n--- RECENT COMPLETED TASKS ---")
        for s in summaries:
            full_res = mempalace.mcp_server.tool_get_drawer(s["drawer_id"])
            if "content" in full_res:
                try:
                    sm = json.loads(full_res["content"])
                    context_blocks.append(f"- Feature '{sm['feature']}': {sm['summary']} (Files: {', '.join(sm['files'])})")
                except Exception:
                    context_blocks.append(f"- {full_res['content']}")
                    
    return {"context": "\n".join(context_blocks)}

# ==================== MCP PROTOCOL HANDLING ====================

TOOLS = {
    "gateway_status": {
        "description": "Get status of the memory gateway, current active feature, and count of layered memory.",
        "input_schema": {"type": "object", "properties": {}},
        "handler": tool_status,
    },
    "gateway_set_active_feature": {
        "description": "Set the current active feature or scope of development.",
        "input_schema": {
            "type": "object",
            "properties": {
                "feature_name": {"type": "string", "description": "e.g., 'feature/auth' or 'refactor/billing'"},
                "project_name": {"type": "string", "description": "Project identifier (optional)"}
            },
            "required": ["feature_name"]
        },
        "handler": tool_set_active_feature,
    },
    "gateway_add_adr": {
        "description": "File a new Architecture Decision Record (ADR) explaining why a technology or design choice was made.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Decision title (e.g. 'PostgreSQL for main DB')"},
                "reason": {"type": "string", "description": "Why this decision was taken"},
                "status": {"type": "string", "description": "accepted, proposed, superseded"}
            },
            "required": ["title", "reason"]
        },
        "handler": tool_add_adr,
    },
    "gateway_add_knowledge": {
        "description": "File stable project knowledge (e.g. configurations, stack details, environment URLs).",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the knowledge detail"},
                "description": {"type": "string", "description": "Detailed explanation"},
                "category": {"type": "string", "description": "e.g., 'database', 'auth', 'deployment'"}
            },
            "required": ["title", "description"]
        },
        "handler": tool_add_knowledge,
    },
    "gateway_add_task": {
        "description": "File or update the state of a development task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_description": {"type": "string", "description": "Task details"},
                "status": {"type": "string", "description": "todo, in_progress, done"}
            },
            "required": ["task_description"]
        },
        "handler": tool_add_task,
    },
    "gateway_compress_session": {
        "description": "Compress session context incrementally. Call this when completing a task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Compact summary of what was built/fixed"},
                "files_modified": {"type": "array", "items": {"type": "string"}, "description": "List of changed files"}
            },
            "required": ["summary"]
        },
        "handler": tool_compress_session,
    },
    "gateway_build_context": {
        "description": "Context Builder. Get highly optimized token context combining ADRs, active tasks, knowledge, and feature status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Semantic query to extract matching knowledge details (optional)"}
            }
        },
        "handler": tool_build_context,
    }
}

SUPPORTED_PROTOCOL_VERSIONS = ["2024-11-05", "2024-03-26"]

def handle_request(request):
    method = request.get("method") or ""
    params = request.get("params") or {}
    req_id = request.get("id")

    if method == "initialize":
        client_version = params.get("protocolVersion", SUPPORTED_PROTOCOL_VERSIONS[-1])
        negotiated = client_version if client_version in SUPPORTED_PROTOCOL_VERSIONS else SUPPORTED_PROTOCOL_VERSIONS[0]
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": negotiated,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mcp-memory-gateway", "version": "1.0.0"},
            },
        }
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {"name": n, "description": t["description"], "inputSchema": t["input_schema"]}
                    for n, t in TOOLS.items()
                ]
            },
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments") or {}
        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }
        try:
            result = TOOLS[tool_name]["handler"](**tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            }
        except Exception as e:
            logger.exception(f"Tool error in {tool_name}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": f"Internal tool error: {str(e)}"},
            }

    if req_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }

def main():
    logger.info("Memory Gateway MCP Server starting...")
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Server loop error: {e}")

if __name__ == "__main__":
    main()
