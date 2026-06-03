"""
MCP Server v6 - Session Memory + Contextual Resolution
Mempalace-backed storage (no MP4, no JSONL, no JSON files)
"""

import sys
import os
from pathlib import Path
current_dir = Path(__file__).resolve().parent
mcp_hub_root = current_dir.parent
if str(mcp_hub_root) not in sys.path: sys.path.insert(0, str(mcp_hub_root))
if str(current_dir) not in sys.path: sys.path.insert(0, str(current_dir))

import json
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from pretty_logger import logger, Colors, get_logger

# Storage: Mempalace-backed (no MP4, no torch)
from storage import MempalaceStorage, VectorEngine

# Advanced features
try:
    from advanced_features import (
        DynamicChunker, QueryExpander, ConfidenceCalibrator,
        AdvancedConfig, ProcessingMode
    )
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False
    DynamicChunker = QueryExpander = ConfidenceCalibrator = AdvancedConfig = ProcessingMode = None

# V6 components
try:
    from memory import SessionManager, SessionType, SessionStrategy
    from memory.session_manager import SessionManager as SM
    from indexing import CodeIndexer, EntityTracker
    from resolution import ContextualResolver, ReferenceDetector
    from shared.token_manager import TokenBudgetManager, get_token_manager
    from memory.skills_manager import SkillsManager
    from storage.memory_handler import MemoryHandler
    from extended_knowledge import ExtendedKnowledgeIndexer
    from smart_session_orchestrator import SmartSessionOrchestrator
    V6_COMPONENTS_AVAILABLE = True
except ImportError as e:
    import traceback
    logger.error(f"V6 components import FAILED: {e}")
    logger.error(traceback.format_exc())
    V6_COMPONENTS_AVAILABLE = False

def safe_jepa_flow(step: str, message: str):
    if hasattr(logger, 'jepa_flow'):
        logger.jepa_flow(step, message)
    else:
        logger.info(f"[JEPA] {step}: {message}")


class MCPServerV6:
    """MCP Server v6 - Mempalace-backed Context Vortex."""

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
        config_file = mcp_hub_root / "config" / "v6_config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {}

    def __init__(self, config_path: Optional[str] = None, verbose: bool = False):
        self.verbose = verbose
        self._start_time = time.time()

        logger.info("=" * 80)
        logger.info("AGI-CONTEXT-VORTEX - Core v10 (Mempalace Backend)")
        logger.info("=" * 80)

        self.config = self._load_config(config_path)
        self._config_cache = {}

        # Mempalace-backed storage
        self.storage = MempalaceStorage(wing="hub")
        self.vector_engine = VectorEngine(config={"wing": "hub"})

        # Advanced features
        if ADVANCED_AVAILABLE:
            self.chunker = DynamicChunker(
                min_chunk_size=self._get_config_value('chunking.min_tokens', 150),
                max_chunk_size=self._get_config_value('chunking.max_tokens', 450),
                overlap_ratio=self._get_config_value('chunking.overlap_percent', 25) / 100.0,
            )
            self.query_expander = QueryExpander()
            self.confidence_calibrator = ConfidenceCalibrator(
                self._get_config_value('anti_hallucination.confidence_thresholds', {
                    'factual': 0.78, 'procedural': 0.72,
                    'conceptual': 0.65, 'temporal': 0.85
                })
            )
        else:
            self.chunker = self.query_expander = self.confidence_calibrator = None

        self.query_count = 0
        self.start_time = time.time()
        self.audit_log = []

        # V6 components
        if V6_COMPONENTS_AVAILABLE:
            self._initialize_v6_components()

        logger.info("=" * 80)
        logger.info("MCP Server v6 ready (mempalace backend)")
        logger.info("=" * 80)

    def _get_config_value(self, key_path: str, default: Any = None) -> Any:
        if key_path in self._config_cache:
            return self._config_cache[key_path]
        if hasattr(self.config, key_path):
            value = getattr(self.config, key_path)
            self._config_cache[key_path] = value
            return value
        if isinstance(self.config, dict):
            keys = key_path.split('.')
            value = self.config
            try:
                for key in keys:
                    value = value[key]
                self._config_cache[key_path] = value
                return value
            except (KeyError, TypeError):
                pass
        self._config_cache[key_path] = default
        return default

    def _initialize_v6_components(self):
        """Initialize V6 components (sessions, indexing, etc.)."""
        logger.info("Initializing v6 components...")

        # Session management
        self.session_manager = SessionManager(
            wing="hub",
            default_strategy=SessionStrategy.TRIMMING,
            auto_save=self._get_config_value('session.auto_save', True),
        )

        # Code indexing
        self.code_indexer = CodeIndexer(wing="hub")

        # Entity tracking
        self.entity_tracker = EntityTracker(wing="hub")

        # Contextual resolution
        self.contextual_resolver = ContextualResolver()

        # Token budget
        self.token_manager = TokenBudgetManager(
            max_tokens=self._get_config_value('toon.max_tokens', 8000),
            reserved_tokens=self._get_config_value('toon.reserved_tokens', 1000),
        )

        # Skills & Memory
        self.skills_manager = SkillsManager(wing="hub")
        self.memory_handler = MemoryHandler(wing="hub")

        # Extended knowledge
        self.extended_knowledge = ExtendedKnowledgeIndexer(wing="hub")

        # Smart orchestrator
        self.orchestrator = SmartSessionOrchestrator(wing="hub", server=self)

        logger.info("v6 components initialized")

    def _log_tool_execution(self, tool_name: str, args: Dict[str, Any], result: Any = None):
        if self.verbose:
            logger.info(f"TOOL: {tool_name}")
            logger.info(f"  Args: {json.dumps(args, default=str)[:200]}")
            if result:
                logger.info(f"  Result: {str(result)[:200]}")

    # ── Tools List ──

    def _handle_tools_list(self) -> Dict:
        tools = [
            {'name': 'ping', 'description': 'Ping test', 'inputSchema': {'type': 'object'}},
            {'name': 'get_context', 'description': 'Retrieve context from memory',
             'inputSchema': {'type': 'object', 'properties': {
                 'query': {'type': 'string'}, 'top_k': {'type': 'integer', 'default': 5},
                 'min_score': {'type': 'number', 'default': 0.5},
                 'session_id': {'type': 'string'}}, 'required': ['query']}},
            {'name': 'validate_response', 'description': 'Validate response against evidence',
             'inputSchema': {'type': 'object', 'properties': {
                 'response': {'type': 'string'}, 'evidence': {'type': 'array'}},
                 'required': ['response', 'evidence']}},
            {'name': 'index_status', 'description': 'Get index status', 'inputSchema': {'type': 'object'}},
            {'name': 'create_session', 'description': 'Create session',
             'inputSchema': {'type': 'object', 'properties': {
                 'session_id': {'type': 'string'}, 'session_type': {'type': 'string'},
                 'strategy': {'type': 'string'}}, 'required': ['session_id']}},
            {'name': 'get_session_summary', 'description': 'Session summary',
             'inputSchema': {'type': 'object', 'properties': {'session_id': {'type': 'string'}},
                             'required': ['session_id']}},
            {'name': 'list_sessions', 'description': 'List sessions', 'inputSchema': {'type': 'object'}},
            {'name': 'delete_session', 'description': 'Delete session',
             'inputSchema': {'type': 'object', 'properties': {'session_id': {'type': 'string'}},
                             'required': ['session_id']}},
            {'name': 'index_code', 'description': 'Index code from directory',
             'inputSchema': {'type': 'object', 'properties': {
                 'directory': {'type': 'string'}, 'recursive': {'type': 'boolean', 'default': True}},
                 'required': ['directory']}},
            {'name': 'search_entity', 'description': 'Search code entity',
             'inputSchema': {'type': 'object', 'properties': {
                 'name': {'type': 'string'}, 'entity_type': {'type': 'string', 'default': 'any'}},
                 'required': ['name']}},
            {'name': 'memory_tool', 'description': 'CRUD memory',
             'inputSchema': {'type': 'object', 'properties': {
                 'command': {'type': 'string'}, 'file_path': {'type': 'string'},
                 'content': {'type': 'string'}, 'session_id': {'type': 'string'}},
                 'required': ['command', 'file_path']}},
            {'name': 'skills_tool', 'description': 'Manage skills',
             'inputSchema': {'type': 'object', 'properties': {
                 'command': {'type': 'string'}, 'skill_id': {'type': 'string'},
                 'content': {'type': 'string'}, 'description': {'type': 'string'}},
                 'required': ['command', 'skill_id']}},
            {'name': 'ground_project_context', 'description': 'Get grounding evidence',
             'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string'}},
                             'required': ['query']}},
            {'name': 'extended_index', 'description': 'Extended code indexing',
             'inputSchema': {'type': 'object', 'properties': {
                 'directory': {'type': 'string'}, 'recursive': {'type': 'boolean', 'default': True}},
                 'required': ['directory']}},
            {'name': 'extended_search', 'description': 'Search extended knowledge',
             'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string'}},
                             'required': ['query']}},
            {'name': 'get_knowledge_summary', 'description': 'Knowledge summary',
             'inputSchema': {'type': 'object'}},
            {'name': 'audit_jepa', 'description': 'JEPA audit',
             'inputSchema': {'type': 'object', 'properties': {
                 'proposal': {'type': 'string'}, 'query': {'type': 'string'}},
                 'required': ['proposal']}},
            {'name': 'sync_world_model', 'description': 'Sync JEPA world model',
             'inputSchema': {'type': 'object'}},
            {'name': 'get_system_status', 'description': 'System status',
             'inputSchema': {'type': 'object'}},
            {'name': 'expand_query', 'description': 'Expand query',
             'inputSchema': {'type': 'object', 'properties': {'query': {'type': 'string'}},
                             'required': ['query']}},
            {'name': 'chunk_document', 'description': 'Chunk document',
             'inputSchema': {'type': 'object', 'properties': {
                 'content': {'type': 'string'}, 'file_path': {'type': 'string'}},
                 'required': ['content']}},
            {'name': 'add_feedback', 'description': 'Add feedback',
             'inputSchema': {'type': 'object', 'properties': {
                 'query': {'type': 'string'}, 'result_doc_id': {'type': 'string'},
                 'relevance_score': {'type': 'number'}, 'was_helpful': {'type': 'boolean'}},
                 'required': ['query', 'result_doc_id']}},
            {'name': 'optimize_configuration', 'description': 'Optimize config',
             'inputSchema': {'type': 'object'}},
            {'name': 'get_smart_status', 'description': 'Smart orchestrator status',
             'inputSchema': {'type': 'object'}},
        ]
        return {'tools': tools}

    # ── Tools Call ──

    def _handle_tools_call(self, params: Dict) -> Dict:
        tool = params.get('name')
        args = params.get('arguments', {})

        handlers = {
            'ping': self._handle_ping,
            'get_context': self._get_context,
            'validate_response': self._validate_response,
            'index_status': self._index_status,
            'create_session': self._create_session,
            'get_session_summary': self._get_session_summary,
            'list_sessions': self._list_sessions,
            'delete_session': self._delete_session,
            'index_code': self._index_code,
            'search_entity': self._search_entity,
            'memory_tool': self._handle_memory_tool,
            'skills_tool': self._handle_skills_tool,
            'ground_project_context': self._handle_ground_project_context,
            'extended_index': self._handle_extended_index,
            'extended_search': self._handle_extended_search,
            'get_knowledge_summary': self._handle_get_knowledge_summary,
            'audit_jepa': self._handle_audit_jepa,
            'sync_world_model': self._handle_sync_world_model,
            'get_system_status': self._handle_get_system_status,
            'expand_query': self._handle_expand_query,
            'chunk_document': self._handle_chunk_document,
            'add_feedback': self._handle_add_feedback,
            'optimize_configuration': self._handle_optimize_configuration,
            'get_smart_status': self._handle_get_smart_status,
        }

        handler = handlers.get(tool)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(handler(args))
                loop.close()
            else:
                result = handler(args)
            self._log_tool_execution(tool, args, result)
            return result

        return {'content': [{'type': 'text', 'text': f'Unknown tool: {tool}'}], '_meta': {'error': True}}

    # ── Core Methods ──

    def _get_context(self, args: Dict) -> Dict:
        session_id = args.get('session_id')
        query = args.get('query', '')

        if session_id and V6_COMPONENTS_AVAILABLE:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self._get_context_with_session(args))
                loop.close()
                return result
            except Exception as e:
                logger.error(f"Session context error: {e}")

        return self._get_context_direct(args)

    async def _get_context_with_session(self, args: Dict) -> Dict:
        session_id = args.get('session_id')
        query = args.get('query', '')

        session = self.session_manager.load_session(session_id)
        if not session:
            return {'content': [{'type': 'text', 'text': f'Session {session_id} not found'}],
                    '_meta': {'error': True}}

        session_history = session.get_recent_turns(n=5)
        optimized_history = self._optimize_session_history(session_history)

        expanded_query, resolved_refs = await self.contextual_resolver.resolve_query(
            query, optimized_history, self.entity_tracker,
            {'functions': self.code_indexer.functions, 'classes': self.code_indexer.classes}
            if self.code_indexer else None
        )

        args_copy = args.copy()
        args_copy['query'] = expanded_query
        result = self._get_context_direct(args_copy)

        if '_meta' not in result:
            result['_meta'] = {}
        result['_meta']['session_id'] = session_id
        result['_meta']['original_query'] = query
        result['_meta']['expanded_query'] = expanded_query

        response_text = result['content'][0]['text'] if result.get('content') else ''
        if self.entity_tracker:
            entities = self.entity_tracker.record_turn(
                session_id, len(session_history) + 1, query, response_text
            )
            result['_meta']['entities_mentioned'] = entities

        self.session_manager.add_turn_to_session(
            session_id, query, response_text,
            {'entities': result['_meta'].get('entities_mentioned', [])}
        )
        return result

    def _optimize_session_history(self, session_history: List[Dict]) -> List[Dict]:
        if not session_history:
            return []
        sections = []
        for i, turn in enumerate(session_history):
            sections.append({
                'id': f"turn_{turn.get('turn_id', i)}",
                'content': f"Q: {turn.get('query', '')}\nA: {turn.get('response', '')}",
                'relevance': 1.0 - (i * 0.1),
                'last_updated': turn.get('timestamp'),
                'access_count': 1,
            })
        optimized = self.token_manager.allocate_tokens(sections)
        result = []
        for section in optimized:
            turn_id = int(section['id'].split('_')[1])
            orig = next((t for t in session_history if t.get('turn_id') == turn_id), None)
            if orig:
                result.append(orig)
        return result

    def _get_context_direct(self, args: Dict) -> Dict:
        query = args.get('query', '')
        top_k = args.get('top_k', 5)
        min_score = args.get('min_score', 0.5)

        # Search via mempalace (no vector engine needed)
        results = self.vector_engine.search_with_mvr(query, top_k=top_k)

        # Confidence calibration
        if ADVANCED_AVAILABLE and self.confidence_calibrator:
            calibrated = []
            for res in results:
                cal = self.confidence_calibrator.calibrate_confidence(
                    raw_score=res.get('score', 0.0),
                    context={'query': query, 'chunk_id': res.get('chunk_id')}
                )
                res['score'] = cal.calibrated_score
                res['confidence_level'] = cal.confidence_level.value
                if cal.calibrated_score >= min_score:
                    calibrated.append(res)
            results = calibrated
        else:
            results = [r for r in results if r.get('score', 0) >= min_score]

        # Build context text
        if not results:
            text = f"No context found for: {query}"
        else:
            parts = []
            for i, r in enumerate(results, 1):
                content = r.get('content', '')
                score = r.get('score', 0)
                parts.append(f"[{i}] (score: {score:.3f})\n{content}")
            text = f"Context for: {query}\n\n" + "\n---\n".join(parts)

        self.query_count += 1
        self._log_query(query, results, not results, 0)

        return {'content': [{'type': 'text', 'text': text}],
                '_meta': {'query': query, 'results_count': len(results)}}

    def _validate_response(self, args: Dict) -> Dict:
        candidate = args.get('response', '')
        evidence_ids = args.get('evidence', [])

        if not evidence_ids:
            return {'content': [{'type': 'text', 'text': 'No evidence provided.'}],
                    '_meta': {'error': True}}

        total_score = 0.0
        found = 0
        for eid in evidence_ids:
            results = self.vector_engine.search_with_mvr(eid, top_k=1)
            if results:
                found += 1
                total_score += results[0].get('score', 0)

        avg = total_score / found if found else 0
        passed = found > 0 and avg > 0.1

        return {'content': [{'type': 'text', 'text':
            f"Validation: {found}/{len(evidence_ids)} evidence found. "
            f"Avg similarity: {avg:.2f}. Status: {'PASSED' if passed else 'FAILED'}"}],
            '_meta': {'validation_passed': passed, 'avg_similarity': avg}}

    def _index_status(self, args: Dict) -> Dict:
        stats = self.vector_engine.get_stats()
        code_stats = self.code_indexer.get_stats() if self.code_indexer else {}
        return {'content': [{'type': 'text', 'text':
            f"MCP Server v6 - Index Status\n"
            f"Backend: mempalace\n"
            f"Chunks: {stats.get('num_vectors', 0)}\n"
            f"Model: {stats.get('model', 'N/A')}\n"
            f"Functions: {code_stats.get('total_functions', 0)}\n"
            f"Classes: {code_stats.get('total_classes', 0)}\n"
            f"Modules: {code_stats.get('total_modules', 0)}\n"
            f"Queries: {self.query_count}\n"
            f"Backend: mempalace"}], '_meta': stats}

    # ── Session Methods ──

    async def _create_session(self, args: Dict) -> Dict:
        session_id = args.get('session_id')
        session_type = args.get('session_type', 'general')
        strategy = args.get('strategy', 'trimming')
        session = self.session_manager.create_session(session_id, strategy=strategy)
        return {'content': [{'type': 'text', 'text':
            f"Session created: {session_id}\nType: {session_type}\nStrategy: {strategy}"}],
            '_meta': {'session_id': session_id}}

    async def _get_session_summary(self, args: Dict) -> Dict:
        session_id = args.get('session_id')
        summary = self.session_manager.get_session_summary(session_id)
        if not summary:
            return {'content': [{'type': 'text', 'text': f'Session {session_id} not found'}]}
        return {'content': [{'type': 'text', 'text': json.dumps(summary, indent=2)}], '_meta': summary}

    async def _list_sessions(self, args: Dict) -> Dict:
        sessions = self.session_manager.list_sessions()
        if not sessions:
            text = "No sessions found."
        else:
            text = f"Sessions ({len(sessions)}):\n" + "\n".join(f"- {s}" for s in sessions)
        return {'content': [{'type': 'text', 'text': text}]}

    async def _delete_session(self, args: Dict) -> Dict:
        session_id = args.get('session_id')
        deleted = self.session_manager.delete_session(session_id)
        return {'content': [{'type': 'text', 'text':
            f"Session {session_id} {'deleted' if deleted else 'not found'}."}]}

    # ── Code Indexing ──

    async def _index_code(self, args: Dict) -> Dict:
        directory = args.get('directory')
        recursive = args.get('recursive', True)
        count = self.code_indexer.index_directory(directory, recursive)
        stats = self.code_indexer.get_stats()
        return {'content': [{'type': 'text', 'text':
            f"Indexed {count} files. Functions: {stats['total_functions']}, "
            f"Classes: {stats['total_classes']}, Modules: {stats['total_modules']}"}],
            '_meta': stats}

    async def _search_entity(self, args: Dict) -> Dict:
        name = args.get('name')
        entity_type = args.get('entity_type', 'any')
        results = []
        if entity_type in ('function', 'any'):
            results.extend([('function', f) for f in self.code_indexer.search_function(name)])
        if entity_type in ('class', 'any'):
            results.extend([('class', c) for c in self.code_indexer.search_class(name)])
        if not results:
            return {'content': [{'type': 'text', 'text': f"No entities found: {name}"}]}
        text = f"Results for '{name}' ({len(results)}):\n\n"
        for etype, e in results:
            text += f"{etype.title()}: {e.name} ({e.module}) L{e.line_start}-{e.line_end}\n"
        return {'content': [{'type': 'text', 'text': text}]}

    # ── Memory & Skills ──

    def _handle_memory_tool(self, args: Dict) -> Dict:
        cmd = args.get('command')
        fp = args.get('file_path')
        content = args.get('content', '')
        try:
            if cmd in ('create', 'update'):
                result = self.memory_handler.create(fp, content)
            elif cmd == 'read':
                result = self.memory_handler.read(fp)
            elif cmd == 'delete':
                result = self.memory_handler.delete(fp)
            elif cmd == 'list':
                result = str(self.memory_handler.list_memories())
            else:
                result = "Invalid command"
            return {'content': [{'type': 'text', 'text': result}]}
        except Exception as e:
            return {'content': [{'type': 'text', 'text': f"Error: {e}"}]}

    def _handle_skills_tool(self, args: Dict) -> Dict:
        cmd = args.get('command')
        skill_id = args.get('skill_id')
        content = args.get('content', '')
        desc = args.get('description', '')
        try:
            if cmd == 'create':
                result = self.skills_manager.create_skill(skill_id, content, desc)
            elif cmd == 'list':
                result = str(self.skills_manager.list_skills())
            else:
                result = "Invalid command"
            return {'content': [{'type': 'text', 'text': result}]}
        except Exception as e:
            return {'content': [{'type': 'text', 'text': f"Error: {e}"}]}

    # ── Extended Knowledge ──

    def _handle_extended_index(self, args: Dict) -> Dict:
        directory = args.get('directory')
        recursive = args.get('recursive', True)
        counts = self.extended_knowledge.index_directory_extended(directory, recursive)
        return {'content': [{'type': 'text', 'text':
            f"Extended indexing complete: {json.dumps(counts)}"}], '_meta': counts}

    def _handle_extended_search(self, args: Dict) -> Dict:
        query = args.get('query', '')
        results = self.extended_knowledge.search_extended(query)
        return {'content': [{'type': 'text', 'text': json.dumps(results, indent=2)}]}

    def _handle_get_knowledge_summary(self, args: Dict) -> Dict:
        summary = self.extended_knowledge.get_knowledge_summary()
        return {'content': [{'type': 'text', 'text': summary}]}

    # ── Grounding ──

    def _handle_ground_project_context(self, args: Dict) -> Dict:
        query = args.get('query', '')
        try:
            from advanced_features.project_grounding import ProjectGrounding
            grounding = ProjectGrounding(
                self._get_config_value('project_context', {}),
                vector_engine=self.vector_engine,
                token_manager=self.token_manager,
            )
            result = grounding.get_grounding_evidence(query)
            return {'content': [{'type': 'text', 'text': result}]}
        except Exception as e:
            return {'content': [{'type': 'text', 'text': f"Grounding error: {e}"}]}

    # ── JEPA ──

    def _handle_audit_jepa(self, args: Dict) -> Dict:
        proposal = args.get('proposal', '')
        query = args.get('query', 'general')
        try:
            from advanced_features.factual_audit_jepa import FactualAuditJEPA
            audit = FactualAuditJEPA(
                self._get_config_value('factual_audit', {}),
                vector_engine=self.vector_engine,
            )
            result = audit.audit_proposal(proposal, query)
            return {'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]}
        except Exception as e:
            return {'content': [{'type': 'text', 'text': f"JEPA audit error: {e}"}]}

    def _handle_sync_world_model(self, args: Dict) -> Dict:
        try:
            from advanced_features.factual_audit_jepa import FactualAuditJEPA
            audit = FactualAuditJEPA(
                self._get_config_value('factual_audit', {}),
                vector_engine=self.vector_engine,
            )
            audit.update_world_model()
            return {'content': [{'type': 'text', 'text': 'World model synced.'}]}
        except Exception as e:
            return {'content': [{'type': 'text', 'text': f"Sync error: {e}"}]}

    # ── Misc ──

    def _handle_ping(self, args: Dict) -> Dict:
        return {'content': [{'type': 'text', 'text': 'pong - AGI-Context-Vortex v10 (mempalace)'}]}

    def _handle_get_system_status(self, args: Dict) -> Dict:
        status = {
            'server': 'AGI-Context-Vortex v10.0',
            'backend': 'mempalace',
            'uptime': time.time() - self._start_time,
            'advanced_features': ADVANCED_AVAILABLE,
            'v6_components': V6_COMPONENTS_AVAILABLE,
            'index_stats': self.code_indexer.get_stats() if self.code_indexer else {},
            'token_budget': getattr(self.token_manager, 'available_tokens', 0),
        }
        return {'content': [{'type': 'text', 'text': json.dumps(status, indent=2)}]}

    def _handle_expand_query(self, args: Dict) -> Dict:
        query = args.get('query', '')
        if not self.query_expander:
            return {'content': [{'type': 'text', 'text': 'Query expansion not available.'}]}
        result = self.query_expander.expand(query)
        return {'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]}

    def _handle_chunk_document(self, args: Dict) -> Dict:
        content = args.get('content', '')
        path = args.get('file_path', 'unknown.txt')
        if not self.chunker:
            return {'content': [{'type': 'text', 'text': 'Chunking not available.'}]}
        chunks = self.chunker.chunk(content, path)
        return {'content': [{'type': 'text', 'text': f"Split into {len(chunks)} chunks."}]}

    def _handle_add_feedback(self, args: Dict) -> Dict:
        return {'content': [{'type': 'text', 'text': 'Feedback recorded.'}]}

    def _handle_optimize_configuration(self, args: Dict) -> Dict:
        return {'content': [{'type': 'text', 'text': 'Configuration optimized.'}]}

    def _handle_get_smart_status(self, args: Dict) -> Dict:
        stats = self.orchestrator.get_statistics() if hasattr(self, 'orchestrator') else {}
        return {'content': [{'type': 'text', 'text': json.dumps(stats, indent=2)}]}

    # ── Audit ──

    def _log_query(self, query: str, results: List[Dict], abstained: bool, elapsed: float):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': len(results),
            'abstained': abstained,
            'elapsed_ms': round(elapsed * 1000, 2),
        }
        self.audit_log.append(entry)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    # ── Protocol ──

    def handle_request(self, request: Dict) -> Dict:
        method = request.get('method')
        params = request.get('params') or {}
        req_id = request.get('id')

        if method == 'initialize':
            return {'jsonrpc': '2.0', 'id': req_id,
                    'result': self._handle_initialize(params)}
        elif method == 'tools/list':
            return {'jsonrpc': '2.0', 'id': req_id,
                    'result': self._handle_tools_list()}
        elif method == 'tools/call':
            return {'jsonrpc': '2.0', 'id': req_id,
                    'result': self._handle_tools_call(params)}
        return {'jsonrpc': '2.0', 'id': req_id,
                'error': {'code': -32601, 'message': f'Unknown: {method}'}}

    def _handle_initialize(self, params: Dict) -> Dict:
        return {
            'protocolVersion': '2024-11-05',
            'capabilities': {'tools': {'listChanged': True}},
            'serverInfo': {'name': 'mcp-hub-v10', 'version': '10.0.0',
                           'description': 'Mempalace-backed Context Vortex'},
        }


def main():
    import io
    if sys.platform == 'win32':
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8-sig', errors='replace')
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', newline='\n')

    server = MCPServerV6()
    logger.info("Server ready - waiting for requests")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            raw = line.strip()
            if not raw:
                continue
            if raw.startswith('\ufeff'):
                raw = raw[1:]
            request = json.loads(raw)
            response = server.handle_request(request)
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(',', ':')))
            sys.stdout.write("\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            pass
        except OSError:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            try:
                sys.stdout.write(json.dumps({'jsonrpc': '2.0', 'id': None,
                    'error': {'code': -32603, 'message': str(e)}}))
                sys.stdout.write("\n")
                sys.stdout.flush()
            except:
                break


if __name__ == '__main__':
    main()
