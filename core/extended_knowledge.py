"""
Extended Knowledge - Code intelligence backed by mempalace drawers.
No more JSON files in data/extended_knowledge/.
"""
import ast
import os
import re
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

import structlog

logger = structlog.get_logger()


@dataclass
class ConstantInfo:
    name: str
    module: str
    value_type: str
    value_preview: str
    line: int
    is_configuration: bool = False


@dataclass
class APIEndpointInfo:
    path: str
    method: str
    function_name: str
    module: str
    line: int
    framework: str
    docstring: str = ""


@dataclass
class ModelInfo:
    name: str
    module: str
    model_type: str
    fields: List[str] = field(default_factory=list)
    line: int = 0
    docstring: str = ""


@dataclass
class PatternInfo:
    pattern_name: str
    module: str
    class_name: str
    confidence: float
    evidence: str = ""


@dataclass
class TodoItem:
    type: str
    text: str
    module: str
    line: int
    priority: str = "medium"


@dataclass
class DependencyInfo:
    source_module: str
    target_module: str
    import_type: str
    items_imported: List[str] = field(default_factory=list)


class QualityGuardian:
    """Code quality principles (no storage needed)."""

    def get_reminder(self) -> str:
        return ("Quality principles: Write tests first. "
                "Keep functions small. Document public APIs. "
                "Handle errors explicitly. No magic.")

    def get_principles_summary(self) -> str:
        return self.get_reminder()

    def check_code_quality(self, code: str) -> List[Dict]:
        issues = []
        if len(code.split("\n")) > 50:
            issues.append({"rule": "function_length",
                           "severity": "warning",
                           "message": "Code exceeds 50 lines"})
        if "TODO" in code:
            issues.append({"rule": "todo_found",
                           "severity": "info",
                           "message": "Contains TODO comments"})
        return issues


class ExtendedKnowledgeIndexer:
    """Extended knowledge indexer backed by mempalace drawers."""

    def __init__(self, wing: str = "hub", index_dir: str = None, **kwargs):
        self.wing = wing
        self.constants: Dict[str, ConstantInfo] = {}
        self.endpoints: Dict[str, APIEndpointInfo] = {}
        self.models: Dict[str, ModelInfo] = {}
        self.patterns: Dict[str, PatternInfo] = {}
        self.todos: List[TodoItem] = []
        self.dependencies: List[DependencyInfo] = []
        self.project_structure: Dict[str, Any] = {}
        self.last_indexed: Optional[str] = None

    def index_file_extended(self, file_path: str) -> Dict[str, int]:
        """Index extended knowledge from a file."""
        counts = {"constants": 0, "endpoints": 0, "models": 0,
                  "patterns": 0, "todos": 0, "dependencies": 0}
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
        except (SyntaxError, OSError):
            return counts

        module = os.path.basename(file_path).replace(".py", "")

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        ci = ConstantInfo(
                            name=target.id, module=module,
                            value_type=type(node.value).__name__,
                            value_preview=ast.dump(node.value)[:100],
                            line=node.lineno,
                            is_configuration=target.id.startswith(("CONFIG", "Settings")),
                        )
                        self.constants[f"{module}.{target.id}"] = ci
                        counts["constants"] += 1
            elif isinstance(node, ast.ClassDef):
                bases = [ast.dump(b) for b in node.bases]
                if any("Model" in b or "Schema" in b for b in bases):
                    methods = [n.name for n in node.body
                               if isinstance(n, ast.FunctionDef)]
                    mi = ModelInfo(
                        name=node.name, module=module,
                        model_type="pydantic" if any("BaseModel" in b for b in bases) else "dataclass",
                        fields=[a.arg for n in node.body if isinstance(n, ast.FunctionDef) for a in n.args.args],
                        line=node.lineno,
                        docstring=ast.get_docstring(node) or "",
                    )
                    self.models[f"{module}.{node.name}"] = mi
                    counts["models"] += 1

        for i, line in enumerate(source.split("\n"), 1):
            for tag in ["TODO", "FIXME", "HACK", "XXX"]:
                if tag in line:
                    self.todos.append(TodoItem(
                        type=tag, text=line.strip()[:200],
                        module=module, line=i,
                    ))
                    counts["todos"] += 1

        # Store in mempalace
        from .mempalace_backend import add_drawer, Room
        content = json.dumps({
            "type": "extended_index", "module": module,
            "file_path": file_path, "counts": counts,
            "constants": [asdict(c) for c in self.constants.values()
                          if c.module == module],
            "models": [asdict(m) for m in self.models.values()
                       if m.module == module],
            "todos": [asdict(t) for t in self.todos
                      if t.module == module],
        }, default=str)
        add_drawer(wing=self.wing, room=Room.EXTENDED,
                   content=content, source_file=file_path)
        return counts

    def index_directory_extended(self, directory: str,
                                 recursive: bool = True) -> Dict[str, int]:
        """Index extended knowledge from directory."""
        total = {"constants": 0, "endpoints": 0, "models": 0,
                 "patterns": 0, "todos": 0, "dependencies": 0}
        exclude = {"__pycache__", ".git", "node_modules", "venv", "data"}
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                if f.endswith(".py"):
                    fp = os.path.join(root, f)
                    counts = self.index_file_extended(fp)
                    for k in total:
                        total[k] += counts.get(k, 0)
            if not recursive:
                break
        self.last_indexed = datetime.now().isoformat()
        self.project_structure = {
            "directory": directory,
            "files_indexed": sum(total.values()),
        }
        return total

    def save_index(self) -> bool:
        """Save is handled automatically by mempalace drawers."""
        return True

    def load_index(self) -> bool:
        """Load is handled automatically by mempalace search."""
        return True

    def search_extended(self, query: str) -> List[Dict[str, Any]]:
        """Search extended knowledge."""
        results = []
        for name, ci in self.constants.items():
            if query.lower() in name.lower():
                results.append({"type": "constant", "name": ci.name,
                                "module": ci.module, "line": ci.line,
                                "value_preview": ci.value_preview})
        for name, mi in self.models.items():
            if query.lower() in name.lower():
                results.append({"type": "model", "name": mi.name,
                                "module": mi.module, "line": mi.line,
                                "docstring": mi.docstring[:200]})
        for t in self.todos:
            if query.lower() in t.text.lower():
                results.append({"type": "todo", "text": t.text,
                                "module": t.module, "line": t.line})
        # Fallback to mempalace search
        if not results:
            from .mempalace_backend import search, Room
            mp_results = search(query=query, wing=self.wing, room=Room.EXTENDED,
                                limit=10)
            for r in mp_results:
                try:
                    data = json.loads(r.get("content", "{}"))
                    results.append({"type": "extended", "module": data.get("module", ""),
                                    "data": data})
                except (json.JSONDecodeError, TypeError):
                    continue
        return results

    def get_knowledge_summary(self) -> str:
        """Get summary of indexed knowledge."""
        return (f"Extended knowledge: {len(self.constants)} constants, "
                f"{len(self.endpoints)} endpoints, {len(self.models)} models, "
                f"{len(self.patterns)} patterns, {len(self.todos)} TODOs, "
                f"{len(self.dependencies)} dependencies")
