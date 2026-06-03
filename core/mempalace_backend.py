"""
Mempalace Backend - Unified storage layer replacing MP4, JSONL, JSON, SQLite.

All persistence flows through mempalace (ChromaDB + SQLite KG).
No more MP4 files, no more JSONL sessions, no more scattered JSON files.

Architecture:
  Wing = project name
  Room = data category
  Drawers = individual data chunks (auto-indexed for semantic search)
  KG = entity relationships with temporal validity
"""
import json
import hashlib
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Lazy mempalace imports – avoids loading heavy deps at module level
# ---------------------------------------------------------------------------
_mp = None  # mempalace.mcp_server module


def _get_mp():
    """Lazy-load mempalace.mcp_server."""
    global _mp
    if _mp is None:
        import mempalace.mcp_server as _mod
        _mp = _mod
    return _mp


def _tool(name: str):
    """Get a mempalace tool function by name."""
    return getattr(_get_mp(), name)


# ---------------------------------------------------------------------------
# Room constants
# ---------------------------------------------------------------------------
class Room:
    """Standard mempalace rooms for HUB."""
    SESSIONS = "sessions"
    CODE = "code"
    CODE_INDEX = "code_index"
    FUNCTIONS = "functions"
    CLASSES = "classes"
    MODULES = "modules"
    EXTENDED = "extended"
    KNOWLEDGE = "knowledge"
    SKILLS = "skills"
    CONTEXT = "context"
    DECISIONS = "decisions"
    TASKS = "tasks"
    SUMMARIES = "summaries"
    EVENTS = "events"
    ENTITIES = "entities"
    CHECKPOINTS = "checkpoints"
    MEMORY = "memory"


# ---------------------------------------------------------------------------
# Low-level primitives
# ---------------------------------------------------------------------------

def _drawer_id(wing: str, room: str, content: str) -> str:
    """Deterministic drawer ID (matches mempalace internal scheme)."""
    h = hashlib.sha256(f"{wing}{room}{content}".encode()).hexdigest()[:24]
    return f"drawer_{wing}_{room}_{h}"


def add_drawer(wing: str, room: str, content: str,
               source_file: str = "", added_by: str = "hub") -> str:
    """File a drawer into mempalace. Returns drawer_id."""
    fn = _tool("tool_add_drawer")
    return fn(wing=wing, room=room, content=content,
              source_file=source_file, added_by=added_by)


def search(query: str, wing: str = None, room: str = None,
           limit: int = 10, max_distance: float = 1.5) -> List[Dict]:
    """Semantic search. Returns list of dicts with drawer content + score."""
    fn = _tool("tool_search")
    return fn(query=query, wing=wing, room=room,
              limit=limit, max_distance=max_distance)


def list_drawers(wing: str = None, room: str = None,
                 limit: int = 100, offset: int = 0) -> List[Dict]:
    """List drawers. Returns list of drawer metadata dicts."""
    fn = _tool("tool_list_drawers")
    return fn(wing=wing, room=room, limit=limit, offset=offset)


def get_drawer(drawer_id: str) -> Optional[Dict]:
    """Fetch a single drawer by ID."""
    fn = _tool("tool_get_drawer")
    return fn(drawer_id=drawer_id)


def update_drawer(drawer_id: str, content: str = None,
                  wing: str = None, room: str = None) -> bool:
    """Update an existing drawer."""
    fn = _tool("tool_update_drawer")
    try:
        fn(drawer_id=drawer_id, content=content, wing=wing, room=room)
        return True
    except Exception:
        return False


def delete_drawer(drawer_id: str) -> bool:
    """Delete a drawer (irreversible)."""
    fn = _tool("tool_delete_drawer")
    try:
        fn(drawer_id=drawer_id)
        return True
    except Exception:
        return False


def check_duplicate(content: str, threshold: float = 0.9) -> bool:
    """Check if content already exists in palace."""
    fn = _tool("tool_check_duplicate")
    return fn(content=content, threshold=threshold)


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------

def kg_add(subject: str, predicate: str, obj: str,
           valid_from: str = None) -> None:
    """Add a fact triple to the knowledge graph."""
    fn = _tool("tool_kg_add")
    kwargs = {"subject": subject, "predicate": predicate, "object": obj}
    if valid_from:
        kwargs["valid_from"] = valid_from
    fn(**kwargs)


def kg_query(entity: str, direction: str = "both",
             as_of: str = None) -> List[Dict]:
    """Query entity relationships."""
    fn = _tool("tool_kg_query")
    kwargs = {"entity": entity, "direction": direction}
    if as_of:
        kwargs["as_of"] = as_of
    return fn(**kwargs)


def kg_invalidate(subject: str, predicate: str, obj: str,
                  ended: str = None) -> None:
    """Mark a fact as no longer true."""
    fn = _tool("tool_kg_invalidate")
    kwargs = {"subject": subject, "predicate": predicate, "object": obj}
    if ended:
        kwargs["ended"] = ended
    fn(**kwargs)


def kg_timeline(entity: str = None) -> List[Dict]:
    """Get chronological timeline of facts."""
    fn = _tool("tool_kg_timeline")
    if entity:
        return fn(entity=entity)
    return fn()


# ---------------------------------------------------------------------------
# Session Storage (replaces JSONL SessionStorage)
# ---------------------------------------------------------------------------

class MempalaceSession:
    """Session backed by mempalace drawers. Compatible with V10 SessionManager."""

    def __init__(self, session_id: str, wing: str,
                 strategy: str = "trimming", max_turns: int = 8):
        self.session_id = session_id
        self.wing = wing
        self.strategy = strategy
        self.max_turns = max_turns
        self.turns: List[Dict] = []
        self.metadata: Dict = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "turn_count": 0,
            "strategy": strategy,
        }
        self._loaded = False

    def load(self) -> bool:
        """Load session turns from mempalace."""
        if self._loaded:
            return True
        room = f"{Room.SESSIONS}_{self.session_id}"
        drawers = list_drawers(wing=self.wing, room=room, limit=500)
        if not drawers:
            return False
        self.turns = []
        for d in drawers:
            try:
                data = json.loads(d.get("content", "{}"))
                if "query" in data:
                    self.turns.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
        self.turns.sort(key=lambda t: t.get("timestamp", ""))
        self.metadata["turn_count"] = len(self.turns)
        self._loaded = True
        return True

    def add_turn(self, query: str, response: str,
                 metadata: Dict = None) -> None:
        """Add a turn to the session."""
        turn = {
            "turn_id": len(self.turns) + 1,
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            turn.update(metadata)
        self.turns.append(turn)
        self.metadata["turn_count"] = len(self.turns)
        self.metadata["last_updated"] = datetime.now().isoformat()
        # Persist to mempalace
        room = f"{Room.SESSIONS}_{self.session_id}"
        add_drawer(wing=self.wing, room=room,
                   content=json.dumps(turn, default=str),
                   source_file=f"session:{self.session_id}")

    def get_recent_turns(self, n: int = 5) -> List[Dict]:
        """Get last N turns."""
        self.load()
        return self.turns[-n:]

    def to_dict(self) -> Dict:
        """Serialize session."""
        return {
            "session_id": self.session_id,
            "wing": self.wing,
            "strategy": self.strategy,
            "max_turns": self.max_turns,
            "turns": self.turns,
            "metadata": self.metadata,
        }


class MempalaceSessionManager:
    """Session manager backed by mempalace."""

    def __init__(self, wing: str, default_strategy: str = "trimming",
                 auto_save: bool = True, **kwargs):
        self.wing = wing
        self.default_strategy = default_strategy
        self.auto_save = auto_save
        self.active_sessions: Dict[str, MempalaceSession] = {}

    def create_session(self, session_id: str, session_type: str = None,
                       strategy: str = None) -> MempalaceSession:
        """Create or load a session."""
        strat = strategy or self.default_strategy
        session = MempalaceSession(session_id, self.wing, strat)
        session.load()
        self.active_sessions[session_id] = session
        return session

    def load_session(self, session_id: str) -> Optional[MempalaceSession]:
        """Load an existing session."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        session = MempalaceSession(session_id, self.wing)
        if session.load():
            self.active_sessions[session_id] = session
            return session
        return None

    def add_turn_to_session(self, session_id: str, query: str,
                            response: str, **kwargs) -> None:
        """Add a turn to a session."""
        session = self.active_sessions.get(session_id)
        if session:
            session.add_turn(query, response, **kwargs)

    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        drawers = list_drawers(wing=self.wing, room=Room.SESSIONS, limit=200)
        ids = set()
        for d in drawers:
            rid = d.get("metadata", {}).get("room", "")
            if rid.startswith(Room.SESSIONS + "_"):
                sid = rid[len(Room.SESSIONS) + 1:]
                if sid:
                    ids.add(sid)
        return sorted(ids)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        room = f"{Room.SESSIONS}_{session_id}"
        drawers = list_drawers(wing=self.wing, room=room, limit=500)
        for d in drawers:
            delete_drawer(d["id"])
        self.active_sessions.pop(session_id, None)
        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary."""
        session = self.load_session(session_id)
        if not session:
            return None
        return {
            "session_id": session_id,
            "metadata": session.metadata,
            "turn_count": len(session.turns),
            "created_at": session.metadata.get("created_at"),
            "last_updated": session.metadata.get("last_updated"),
        }


# ---------------------------------------------------------------------------
# Memory Handler (replaces file-based MemoryHandler)
# ---------------------------------------------------------------------------

class MempalaceMemoryHandler:
    """Memory CRUD backed by mempalace drawers."""

    def __init__(self, wing: str, **kwargs):
        self.wing = wing

    def create(self, file_path: str, content: str,
               session_id: str = None) -> str:
        """Store a memory."""
        room = Room.MEMORY
        add_drawer(wing=self.wing, room=room, content=content,
                   source_file=file_path, added_by="memory_tool")
        return f"Memory stored: {file_path}"

    def read(self, file_path: str, session_id: str = None) -> str:
        """Read a memory by source file."""
        results = search(query=file_path, wing=self.wing, room=Room.MEMORY,
                         limit=5)
        for r in results:
            if file_path in r.get("content", ""):
                return r["content"]
        return ""

    def delete(self, file_path: str, session_id: str = None) -> str:
        """Delete a memory."""
        results = search(query=file_path, wing=self.wing, room=Room.MEMORY,
                         limit=5)
        for r in results:
            if file_path in r.get("content", ""):
                delete_drawer(r.get("id", ""))
                return f"Memory deleted: {file_path}"
        return f"Memory not found: {file_path}"

    def list_memories(self, session_id: str = None) -> List[str]:
        """List all memories."""
        drawers = list_drawers(wing=self.wing, room=Room.MEMORY, limit=200)
        return [d.get("content", "")[:100] for d in drawers]


# ---------------------------------------------------------------------------
# Code Indexer (replaces JSON-based CodeIndexer)
# ---------------------------------------------------------------------------

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


class MempalaceCodeIndexer:
    """Code indexer backed by mempalace drawers + KG."""

    def __init__(self, wing: str, **kwargs):
        self.wing = wing
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.modules: Dict[str, ModuleInfo] = {}

    def index_file(self, file_path: str) -> bool:
        """Index a Python file via AST."""
        import ast
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
                # Store in mempalace
                content = json.dumps({
                    "type": "function", "name": node.name,
                    "module": module_name, "signature": fi.signature,
                    "line_start": fi.line_start, "line_end": fi.line_end,
                    "docstring": fi.docstring, "parameters": fi.parameters,
                }, default=str)
                add_drawer(wing=self.wing, room=Room.FUNCTIONS,
                           content=content, source_file=file_path)
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
                content = json.dumps({
                    "type": "class", "name": node.name,
                    "module": module_name,
                    "line_start": ci.line_start, "line_end": ci.line_end,
                    "docstring": ci.docstring, "methods": ci.methods,
                }, default=str)
                add_drawer(wing=self.wing, room=Room.CLASSES,
                           content=content, source_file=file_path)

        mi = ModuleInfo(
            name=module_name, file_path=file_path,
            imports=imports, functions=functions, classes=classes,
            last_indexed=datetime.now().isoformat(),
        )
        self.modules[module_name] = mi
        content = json.dumps({
            "type": "module", "name": module_name,
            "file_path": file_path, "functions": functions,
            "classes": classes, "imports": imports,
        }, default=str)
        add_drawer(wing=self.wing, room=Room.MODULES,
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
        results = search(query=name, wing=self.wing, room=Room.FUNCTIONS,
                         limit=10)
        funcs = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("type") == "function":
                    funcs.append(FunctionInfo(**{
                        k: data[k] for k in FunctionInfo.__dataclass_fields__
                        if k in data
                    }))
            except (json.JSONDecodeError, TypeError):
                continue
        # Fallback to in-memory
        if not funcs:
            for k, v in self.functions.items():
                if name.lower() in k.lower():
                    funcs.append(v)
        return funcs

    def search_class(self, name: str) -> List[ClassInfo]:
        """Search classes by name."""
        results = search(query=name, wing=self.wing, room=Room.CLASSES,
                         limit=10)
        classes = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if data.get("type") == "class":
                    classes.append(ClassInfo(**{
                        k: data[k] for k in ClassInfo.__dataclass_fields__
                        if k in data
                    }))
            except (json.JSONDecodeError, TypeError):
                continue
        if not classes:
            for k, v in self.classes.items():
                if name.lower() in k.lower():
                    classes.append(v)
        return classes

    def get_function_location(self, name: str) -> Optional[Dict]:
        """Get function location info."""
        funcs = self.search_function(name)
        if funcs:
            f = funcs[0]
            return {
                "function": f.name, "module": f.module,
                "file": f.module + ".py", "line_start": f.line_start,
                "line_end": f.line_end, "signature": f.signature,
            }
        return None

    def get_stats(self) -> Dict:
        """Get indexer statistics."""
        return {
            "total_modules": len(self.modules),
            "total_functions": len(self.functions),
            "total_classes": len(self.classes),
            "backend": "mempalace",
        }


# ---------------------------------------------------------------------------
# Entity Tracker (replaces JSON-based EntityTracker)
# ---------------------------------------------------------------------------

@dataclass
class EntityMention:
    entity_name: str
    session_id: str
    turn_id: int
    context: str
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            "entity_name": self.entity_name,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class MempalaceEntityTracker:
    """Entity tracker backed by mempalace KG + drawers."""

    def __init__(self, wing: str, code_index: Dict = None, **kwargs):
        self.wing = wing
        self.code_index = code_index or {}
        self.mentions: Dict[str, List[EntityMention]] = {}
        self.session_entities: Dict[str, List[str]] = {}

    def extract_entities_from_text(self, text: str) -> List[str]:
        """Extract entity names from text using code index."""
        entities = []
        for name in list(self.code_index.get("functions", {}).keys()) + \
                     list(self.code_index.get("classes", {}).keys()):
            short = name.split(".")[-1]
            if short in text or name in text:
                entities.append(name)
        return entities

    def record_mention(self, entity_name: str, session_id: str,
                       turn_id: int, context: str) -> None:
        """Record an entity mention."""
        mention = EntityMention(
            entity_name=entity_name, session_id=session_id,
            turn_id=turn_id, context=context[:500],
            timestamp=datetime.now().isoformat(),
        )
        self.mentions.setdefault(entity_name, []).append(mention)
        self.session_entities.setdefault(session_id, []).append(entity_name)
        # Store in KG
        kg_add(subject=session_id, predicate="mentions", obj=entity_name)

    def record_turn(self, session_id: str, turn_id: int,
                    query: str, response: str) -> List[str]:
        """Extract and record entities from a conversation turn."""
        text = f"{query} {response}"
        entities = self.extract_entities_from_text(text)
        for ent in entities:
            self.record_mention(ent, session_id, turn_id, text[:500])
        return entities

    def get_entity_history(self, entity_name: str) -> List[EntityMention]:
        """Get mention history for an entity."""
        return self.mentions.get(entity_name, [])

    def get_related_entities(self, entity_name: str,
                             limit: int = 10) -> List[str]:
        """Get entities that co-occur with given entity."""
        sessions = set()
        for m in self.mentions.get(entity_name, []):
            sessions.add(m.session_id)
        related = set()
        for sid in sessions:
            for e in self.session_entities.get(sid, []):
                if e != entity_name:
                    related.add(e)
        return list(related)[:limit]

    def search_mentions(self, keyword: str) -> Dict[str, List[EntityMention]]:
        """Search mentions by keyword."""
        results = {}
        for name, mentions in self.mentions.items():
            if keyword.lower() in name.lower():
                results[name] = mentions
        return results

    def get_stats(self) -> Dict:
        """Get tracker statistics."""
        return {
            "total_entities_tracked": len(self.mentions),
            "total_mentions": sum(len(v) for v in self.mentions.values()),
            "total_sessions": len(self.session_entities),
            "backend": "mempalace",
        }


# ---------------------------------------------------------------------------
# Extended Knowledge (replaces JSON-based ExtendedKnowledgeIndexer)
# ---------------------------------------------------------------------------

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


class MempalaceExtendedKnowledge:
    """Extended knowledge backed by mempalace drawers."""

    def __init__(self, wing: str, **kwargs):
        self.wing = wing
        self.constants: Dict[str, ConstantInfo] = {}
        self.endpoints: Dict[str, APIEndpointInfo] = {}
        self.models: Dict[str, ModelInfo] = {}
        self.patterns: Dict[str, PatternInfo] = {}
        self.todos: List[TodoItem] = []
        self.dependencies: List[DependencyInfo] = []

    def index_file_extended(self, file_path: str) -> Dict[str, int]:
        """Index extended knowledge from a file."""
        import ast
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
                    if isinstance(target, ast.Name):
                        name = target.id
                        if name.isupper():
                            ci = ConstantInfo(
                                name=name, module=module,
                                value_type=type(node.value).__name__,
                                value_preview=ast.dump(node.value)[:100],
                                line=node.lineno,
                                is_configuration=name.startswith(("CONFIG", "Settings")),
                            )
                            self.constants[f"{module}.{name}"] = ci
                            counts["constants"] += 1
            elif isinstance(node, ast.ClassDef):
                bases = [ast.dump(b) for b in node.bases]
                if any("Model" in b or "Schema" in b for b in bases):
                    methods = [n.name for n in node.body
                               if isinstance(n, ast.FunctionDef)]
                    mi = ModelInfo(
                        name=node.name, module=module,
                        model_type="pydantic" if any("BaseModel" in b for b in bases) else "dataclass",
                        methods=methods,
                        line=node.lineno,
                        docstring=ast.get_docstring(node) or "",
                    )
                    self.models[f"{module}.{node.name}"] = mi
                    counts["models"] += 1

        # TODOs
        for i, line in enumerate(source.split("\n"), 1):
            for tag in ["TODO", "FIXME", "HACK", "XXX"]:
                if tag in line:
                    ti = TodoItem(
                        type=tag, text=line.strip()[:200],
                        module=module, line=i,
                    )
                    self.todos.append(ti)
                    counts["todos"] += 1

        # Store in mempalace
        content = json.dumps({
            "module": module, "file_path": file_path,
            "constants_count": counts["constants"],
            "models_count": counts["models"],
            "todos_count": counts["todos"],
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
        return total

    def search_extended(self, query: str) -> List[Dict[str, Any]]:
        """Search extended knowledge."""
        results = []
        for name, ci in self.constants.items():
            if query.lower() in name.lower():
                results.append({"type": "constant", "name": ci.name,
                                "module": ci.module, "line": ci.line})
        for name, mi in self.models.items():
            if query.lower() in name.lower():
                results.append({"type": "model", "name": mi.name,
                                "module": mi.module, "line": mi.line})
        return results

    def get_knowledge_summary(self) -> str:
        """Get summary of indexed knowledge."""
        return (f"Extended knowledge: {len(self.constants)} constants, "
                f"{len(self.endpoints)} endpoints, {len(self.models)} models, "
                f"{len(self.patterns)} patterns, {len(self.todos)} TODOs, "
                f"{len(self.dependencies)} dependencies")


# ---------------------------------------------------------------------------
# Skills Manager (replaces file-based SkillsManager)
# ---------------------------------------------------------------------------

class MempalaceSkillsManager:
    """Skills manager backed by mempalace drawers."""

    def __init__(self, wing: str, **kwargs):
        self.wing = wing
        self.skills_cache: Dict[str, Dict] = {}

    def create_skill(self, skill_id: str, content: str,
                     description: str = "") -> str:
        """Create a skill."""
        data = json.dumps({
            "skill_id": skill_id, "description": description,
            "content": content, "created_at": datetime.now().isoformat(),
        }, default=str)
        add_drawer(wing=self.wing, room=Room.SKILLS,
                   content=data, added_by="skills_tool")
        self.skills_cache[skill_id] = {"description": description}
        return f"Skill created: {skill_id}"

    def search_skills(self, query: str) -> List[Dict]:
        """Search skills."""
        results = search(query=query, wing=self.wing, room=Room.SKILLS,
                         limit=10)
        skills = []
        for r in results:
            try:
                data = json.loads(r.get("content", "{}"))
                if "skill_id" in data:
                    skills.append(data)
            except (json.JSONDecodeError, TypeError):
                continue
        return skills

    def get_stats(self) -> Dict:
        """Get skills stats."""
        return {
            "total_skills": len(self.skills_cache),
            "backend": "mempalace",
        }


# ---------------------------------------------------------------------------
# Project Grounding
# ---------------------------------------------------------------------------

class MempalaceProjectGrounding:
    """Project grounding backed by mempalace drawers."""

    def __init__(self, wing: str, **kwargs):
        self.wing = wing

    def get_grounding_evidence(self, query: str) -> Dict:
        """Get grounding evidence for a query."""
        results = search(query=query, wing=self.wing, room=Room.CONTEXT,
                         limit=5)
        context = "\n".join(r.get("content", "") for r in results[:3])
        return {
            "query": query,
            "context": context,
            "sources": [r.get("content", "")[:100] for r in results],
            "backend": "mempalace",
        }


# ---------------------------------------------------------------------------
# Smart Session Orchestrator (replaces JSON state file)
# ---------------------------------------------------------------------------

class MempalaceOrchestrator:
    """Orchestrator state backed by mempalace drawers."""

    def __init__(self, wing: str, server=None, **kwargs):
        self.wing = wing
        self.server = server
        self._state: Dict = {
            "project_sessions": {},
            "indexed_projects": {},
            "statistics": {"sessions_created": 0, "sessions_reused": 0},
        }

    def _load_state(self) -> Dict:
        """Load orchestrator state from mempalace."""
        results = search(query="orchestrator_state", wing=self.wing,
                         room=Room.CONTEXT, limit=1)
        if results:
            try:
                self._state = json.loads(results[0].get("content", "{}"))
            except (json.JSONDecodeError, TypeError):
                pass
        return self._state

    def _save_state(self) -> None:
        """Save orchestrator state to mempalace."""
        add_drawer(wing=self.wing, room=Room.CONTEXT,
                   content=json.dumps(self._state, default=str),
                   source_file="orchestrator_state")
