# 🌀 MCP HUB V10 — Context Vortex + V2 Workflow

> **Motor de inteligencia contextual con MCPs especializados, anti-alucinación JEPA, Code Guardian, Memory Gateway y workflow V2 con checkpoints stakeholder.**

---

## 📋 Descripción

Sistema MCP (Model Context Protocol) que combina:

| Capa | Origen | Función |
|------|--------|---------|
| **Context Vortex v10** | [0xC1pher/MCP-HUB-V10](https://github.com/0xC1pher/MCP-HUB-V10) (main + feature/code-guardian) | Engine con 30+ tools: JEPA World Model, Code Guardian, Visual Monitor, Smart Session Orchestrator, PrettyLogger, Vector Storage MP4 |
| **MCPs especializados V2** | HUB local | Architect, Backend Developer, Frontend Developer, Tester, Vision Specialist con workflow de checkpoints stakeholder |
| **Memory Gateway** | HUB local | MemPalace-backed: 7 tools para ADRs, knowledge, tasks, summaries y context builder token-efficient |
| **Vision Hub** | HUB local | FastVLM-WebGPU (browser-side) + Playwright server-side para análisis multimodal |

---

## 🚀 Inicio Rápido

```powershell
# Server principal (V10 con todas las tools)
python -m core.mcp_http_server

# Gateway de memoria (mempalace, segundo proceso MCP)
python -m core.mcp_memory_gateway

# Workflow V2 con checkpoints
python tests/integration/test_workflow_with_checkpoints.py
```

---

## 📁 Estructura

```
HUB/
├── core/
│   ├── mcp_http_server.py          # V10: server principal (30+ tools)
│   ├── mcp_memory_gateway.py       # MemPalace gateway (7 tools)
│   ├── v6.py                       # V6 engine (TOON, sessions, retrieval)
│   ├── smart_session_orchestrator.py
│   ├── visual_monitor.py           # Matrix-style visual logs
│   ├── pretty_logger.py
│   ├── log_config.py
│   ├── extended_knowledge.py
│   ├── advanced_features/
│   │   ├── code_guardian_mcp.py    # Code quality guardian (nuevo)
│   │   ├── decorators.py
│   │   ├── confidence_calibration.py
│   │   ├── dynamic_chunking.py
│   │   ├── factual_audit_jepa.py   # JEPA World Model
│   │   ├── multi_vector_retrieval.py
│   │   ├── orchestrator.py
│   │   ├── project_grounding.py
│   │   ├── project_knowledge.py
│   │   ├── query_expansion.py
│   │   ├── virtual_chunk_system.py
│   │   └── run_system.py
│   ├── workflow/                   # V2: Checkpoints & markdown reader
│   │   ├── checklist_manager.py
│   │   ├── checkpoint_handler.py
│   │   └── markdown_reader.py
│   ├── vision/                     # FastVLM server
│   │   └── vision_hub.py
│   ├── llm/                        # Model router (Ollama)
│   │   ├── model_router.py
│   │   ├── prompt_manager.py
│   │   └── provider.py
│   ├── memory/                     # Hybrid: V10 sessions + HUB event-sourcing
│   │   ├── event_store.py          # HUB: SQLite event store
│   │   ├── memory_engine.py        # HUB: conflict resolution
│   │   ├── rollback_manager.py     # HUB: snapshots
│   │   ├── session_manager.py      # V10: smart sessions
│   │   ├── skills_manager.py       # V10: skills persistence
│   │   ├── summarizing_session.py  # V10
│   │   └── trimming_session.py     # V10
│   ├── communication/              # HUB: retry/circuit breaker
│   │   ├── protocol.py
│   │   └── circuit_breaker.py
│   ├── performance/                # HUB: psutil monitor
│   │   └── monitor.py
│   ├── toon/                       # HUB: token budget
│   │   └── token_budget.py
│   ├── storage/                    # V10: MP4 vector storage
│   │   ├── mp4_storage.py
│   │   ├── vector_engine.py
│   │   ├── session_storage.py
│   │   ├── compressed_mp4_storage.py
│   │   ├── compressed_storage.py
│   │   └── memory_handler.py
│   ├── resolution/                 # V10: contextual resolution
│   │   ├── contextual_resolver.py
│   │   └── reference_detector.py
│   ├── indexing/                   # V10: code indexer
│   │   ├── code_indexer.py
│   │   └── entity_tracker.py
│   └── shared/                     # V10: shared utilities
│       ├── advanced_scorer.py
│       ├── safety_system.py
│       ├── semantic_chunker.py
│       └── token_manager.py
│
├── mcps/                           # HUB: Specialized agents
│   ├── base_mcp.py
│   ├── architect_mcp.py
│   ├── backend_developer_mcp.py    # V2: APIs, DB models
│   ├── frontend_developer_mcp.py   # V2: UI components
│   ├── developer_mcp.py            # Legacy: kept for compat
│   ├── tester_mcp.py
│   ├── vision_specialist_mcp.py
│   ├── vision_specialist_mcp_optional.py  # Lazy-loaded
│   └── contracts/
│       ├── architect_contracts.py
│       ├── backend_developer_contracts.py
│       ├── frontend_developer_contracts.py
│       ├── developer_contracts.py  # Legacy
│       └── tester_contracts.py
│
├── config/
│   ├── v6_config.json              # V10 storage config
│   ├── server_config.json
│   ├── toon/                       # HUB: Specialized TOONs
│   │   ├── architect.toon
│   │   ├── backend_developer.toon
│   │   ├── frontend_developer.toon
│   │   ├── developer.toon           # Legacy
│   │   ├── tester.toon
│   │   ├── orchestrator.toon
│   │   └── global_rules.toon
│   └── ...
│
├── fastvlm-webgpu/                 # HUB: Browser-side vision client
│   ├── index.html
│   ├── js/main.js
│   └── styles/main.css
│
├── data/                           # Runtime data (gitignored)
│   ├── sessions/
│   ├── project_context/
│   ├── skills/
│   ├── memories/
│   ├── smart_sessions/
│   ├── extended_knowledge/
│   └── *.mp4 (vector storage)
│
├── tests/                          # V10 tests + HUB V2 tests
│   ├── test_mcp_connection.py      # V10
│   ├── test_v6_only.py             # V10
│   ├── test_protocol.py            # V10
│   ├── integration/                # HUB V2
│   │   ├── test_workflow_simple.py
│   │   └── test_workflow_with_checkpoints.py
│   └── unit/                       # HUB
│       ├── test_circuit_breaker.py
│       ├── test_event_store.py
│       ├── test_memory_engine.py
│       └── ...
│
└── docs/                           # V10 documentation
    ├── V8_USER_GUIDE.md
    ├── V8_TECHNICAL_DOCUMENTATION.md
    ├── V8_CHANGES_SUMMARY.md
    └── diagrama.md
```

---

## 🔧 Tools Expuestas (V10)

### Core & Retrieval
- `ping`, `get_context`, `validate_response`, `index_status`

### Smart Session
- `smart_session_init`, `smart_query`, `get_smart_status`
- `create_session`, `list_sessions`, `get_session_summary`, `delete_session`

### JEPA World Model & Grounding
- `audit_jepa`, `sync_world_model`, `ground_project_context`
- `check_quality`, `get_quality_principles`

### Code Guardian (nuevo)
- `check_code_creation`, `check_code_modification`, `check_code_deletion`

### Persistence & Skills
- `memory_tool`, `skills_tool`

### Code Intelligence
- `index_code`, `extended_index`, `search_entity`, `extended_search`

### Advanced Processing
- `process_advanced`, `get_knowledge_summary`, `expand_query`
- `chunk_document`, `optimize_configuration`, `add_feedback`

### System
- `get_system_status`, `test_colors_flow`

## 🧠 Memory Gateway (7 tools)

- `gateway_status` — Estado del gateway
- `gateway_set_active_feature` — Define feature activa
- `gateway_add_adr` — Registra ADR (Architecture Decision Record)
- `gateway_add_knowledge` — Conocimiento estable del proyecto
- `gateway_add_task` — Tareas de desarrollo con estado
- `gateway_compress_session` — Comprime sesión incrementalmente
- `gateway_build_context` — **Context builder** (queries ADRs/tasks/knowledge y devuelve prompt compacto)

---

## 🔄 Flujo V2 con Checkpoints

```
Usuario → [requirements.md] → OrchestratorV2 (TODO: portar a V10)
  ↓
MarkdownReader → parse requerimientos
  ↓
ChecklistManager → crea tareas
  ↓
Tarea 1: ArchitectMCP → checkpoint → user APPROVE
Tarea 2: BackendDeveloperMCP → checkpoint → user APPROVE
Tarea 3: FrontendDeveloperMCP → checkpoint → user APPROVE
Tarea 4: TesterMCP → checkpoint → user APPROVE
```

El `core/orchestrator_v2.py` necesita ser portado para integrarse con el V10 server. Por ahora los tests V2 están en `tests/integration/test_workflow_with_checkpoints.py` y funcionan standalone.

---

## 📦 Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

Para el Memory Gateway:
```bash
pip install mempalace
```

---

## 🌿 Branches

- `main` — Stable (V10 base + Code Guardian merged)
- `origin/feature/code-guardian-mcp-integration` — Ya mergeado en main

---

## 📚 Documentación Adicional

- [V10 README original](README.md) (en este mismo directorio)
- [V10 Anti-Alucinación](V9_ANTI_ALUCINACION_ANALISIS.md)
- [V8 User Guide](docs/V8_USER_GUIDE.md)
- [V8 Technical](docs/V8_TECHNICAL_DOCUMENTATION.md)
- [HUB V2 Workflow](IMPLEMENTACION_FLUJO_CORRECTO.md)
- [HUB V2 Workflow (agent)](.agent/workflows/NUEVO_FLUJO_CORRECTO.md)
- [Migración docs](FLUJO_DOCUMENTACION_STATUS.md)
- [Feature tracking](feat.md)

---

**Versión**: V10 + HUB V2 merge  
**Última actualización**: 2026-06-03
