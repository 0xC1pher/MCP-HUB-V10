"""
Code Indexer - AST-based code indexer backed by mempalace drawers.
"""
import ast
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class FunctionInfo:
    name: str
    module: str
    signature: str
    line_start: int
    line_end: int
    docstring: str
    parameters: List[str] = field(default_factory=list)
    returns: str = ""
    decorators: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    module: str
    line_start: int
    line_end: int
    docstring: str
    methods: List[str] = field(default_factory=list)
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)


@dataclass
class ModuleInfo:
    name: str
    file_path: str
    imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    last_indexed: str = ""


class CodeIndexer:
    """Code indexer backed by mempalace drawers."""

    def __init__(self, wing: str = "hub", index_dir: str = None, **kwargs):
        self.wing = wing
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.modules: Dict[str, ModuleInfo] = {}

    def index_file(self, file_path: str) -> bool:
        """Index a Python file via AST."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
            tree = ast.parse(source, filename=file_path)
        except (SyntaxError, OSError):
            return False

        module_name = os.path.basename(file_path).replace(".py", "")
        imports = []
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.dump(node))
            elif isinstance(node, ast.FunctionDef):
                fi = FunctionInfo(
                    name=node.name,
                    module=module_name,
                    signature=f"def {node.name}(...)",
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    docstring=ast.get_docstring(node) or "",
                    parameters=[a.arg for a in node.args.args],
                    decorators=[ast.dump(d) for d in node.decorator_list],
                )
                self.functions[f"{module_name}.{node.name}"] = fi
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                ci = ClassInfo(
                    name=node.name,
                    module=module_name,
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    docstring=ast.get_docstring(node) or "",
                    methods=[n.name for n in node.body
                             if isinstance(n, ast.FunctionDef)],
                    bases=[ast.dump(b) for b in node.bases],
                    decorators=[ast.dump(d) for d in node.decorator_list],
                )
                self.classes[f"{module_name}.{node.name}"] = ci
                classes.append(node.name)

        mi = ModuleInfo(
            name=module_name, file_path=file_path,
            imports=imports, functions=functions, classes=classes,
            last_indexed=datetime.now().isoformat(),
        )
        self.modules[module_name] = mi

        # Store in mempalace
        from ..mempalace_backend import add_drawer, Room
        content = json.dumps({
            "type": "code_index", "module": module_name,
            "file_path": file_path, "functions": functions,
            "classes": classes, "imports_count": len(imports),
        }, default=str)
        add_drawer(wing=self.wing, room=Room.CODE_INDEX,
                   content=content, source_file=file_path)
        return True

    def index_directory(self, directory: str, recursive: bool = True,
                        exclude_dirs: List[str] = None) -> int:
        """Index all Python files in a directory."""
        exclude = set(exclude_dirs or ["__pycache__", ".git", "node_modules",
                                       "venv", ".venv", "data"])
        count = 0
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in exclude]
            for f in files:
                if f.endswith(".py"):
                    fp = os.path.join(root, f)
                    if self.index_file(fp):
                        count += 1
            if not recursive:
                break
        return count

    def search_function(self, name: str) -> List[FunctionInfo]:
        """Search functions by name."""
        results = []
        for k, v in self.functions.items():
            if name.lower() in k.lower():
                results.append(v)
        return results

    def search_class(self, name: str) -> List[ClassInfo]:
        """Search classes by name."""
        results = []
        for k, v in self.classes.items():
            if name.lower() in k.lower():
                results.append(v)
        return results

    def get_function_location(self, name: str) -> Optional[Dict]:
        """Get function location."""
        for k, v in self.functions.items():
            if name.lower() in k.lower():
                return {
                    "function": v.name, "module": v.module,
                    "file": v.module + ".py", "line_start": v.line_start,
                    "line_end": v.line_end, "signature": v.signature,
                }
        return None

    def save_index(self) -> bool:
        """Save is handled by mempalace."""
        return True

    def load_index(self) -> bool:
        """Load from mempalace on demand."""
        return True

    def get_stats(self) -> Dict:
        """Get indexer statistics."""
        return {
            "total_modules": len(self.modules),
            "total_functions": len(self.functions),
            "total_classes": len(self.classes),
            "backend": "mempalace",
        }
