# 🌀 MCP HUB V11 — Context Vortex (Mempalace Backend)

> **Motor de inteligencia contextual con MCPs especializados, anti-alucinación JEPA, Code Guardian, Memory Gateway y workflow V2 — todo persistido en Mempalace (ChromaDB + SQLite KG).**

---

## Descripcion

Sistema MCP (Model Context Protocol) que combina:

| Capa | Funcion |
|------|---------|
| **Context Vortex v11** | Engine con 25+ tools: JEPA World Model, Code Guardian, Smart Session Orchestrator, PrettyLogger — **sin torch ni sentence-transformers** |
| **MCPs especializados V2** | Architect, Backend Developer, Frontend Developer, Tester, Vision Specialist con workflow de checkpoints stakeholder |
| **Memory Gateway** | MemPalace-backed: 7 tools para ADRs, knowledge, tasks, summaries y context builder |
| **Vision Hub** | FastVLM-WebGPU (browser-side) + Playwright server-side |
| **Mempalace Backend** | Backend unificado de storage: reemplaza MP4, JSONL, JSON, SQLite — todo en ChromaDB + KG |

---

## Que cambia en V11

| V10 | V11 |
|-----|-----|
| `data/*.mp4` (vector storage) | MemPalace drawers |
| `data/sessions/*.jsonl` | MemPalace drawers |
| `data/memories/*.txt` | MemPalace drawers |
| `data/events.db` (SQLite) | MemPalace KG |
| `data/checkpoints/*.json` | MemPalace drawers |
| `data/code_index/*.json` | MemPalace drawers + KG |
| `data/extended_knowledge/*.json` | MemPalace drawers |
| `torch` (~4GB) | Eliminado |
| `sentence-transformers` | Eliminado |
| `hnswlib` | Eliminado |
| `pymp4` | Eliminado |

---

## Inicio Rapido

```powershell
# Server principal (V11 con mempalace backend)
python -m core.mcp_http_server

# Gateway de memoria (mempalace, segundo proceso MCP)
python -m core.mcp_memory_gateway
```

---

## Arquitectura Mempalace

```
Wing: "{project_name}"
  Room: "sessions"      -> Historial de conversaciones
  Room: "code_index"    -> Indice de funciones/clases/modulos
  Room: "functions"     -> Funciones indexadas
  Room: "classes"       -> Clases indexadas
  Room: "modules"       -> Modulos indexados
  Room: "extended"      -> Conocimiento extendido (endpoints, constants, patterns)
  Room: "knowledge"     -> Conocimiento estable
  Room: "skills"        -> Skills de agentes
  Room: "context"       -> Contexto del proyecto
  Room: "decisions"     -> ADRs
  Room: "tasks"         -> Tareas con estado
  Room: "summaries"     -> Resumenes de sesion
  Room: "events"        -> Eventos del sistema
  Room: "checkpoints"   -> Puntos de rollback
  Room: "memory"        -> Memoria persistente
  Room: "code"          -> Code chunks para search

KG: Relaciones temporales (entity triples)
```

---

## Estructura

```
HUB/
├── core/
│   ├── mempalace_backend.py         # Backend unificado (NUEVO V11)
│   ├── mcp_http_server.py           # Server principal (25+ tools)
│   ├── mcp_memory_gateway.py        # MemPalace gateway (7 tools)
│   ├── v6.py                        # Engine principal (mempalace-backed)
│   ├── smart_session_orchestrator.py
│   ├── visual_monitor.py
│   ├── pretty_logger.py
│   ├── extended_knowledge.py        # Indexador extendido
│   ├── advanced_features/
│   │   ├── code_guardian_mcp.py
│   │   ├── confidence_calibration.py
│   │   ├── dynamic_chunking.py
│   │   ├── factual_audit_jepa.py
│   │   ├── multi_vector_retrieval.py
│   │   ├── query_expansion.py
│   │   └── ...
│   ├── storage/
│   │   ├── mempalace_storage.py     # Reemplaza MP4 + VectorEngine (NUEVO V11)
│   │   ├── session_storage.py       # Wrapper mempalace sessions
│   │   ├── memory_handler.py        # Wrapper mempalace memory
│   │   ├── mp4_storage.py           # Redirect a mempalace
│   │   └── vector_engine.py         # Redirect a mempalace
│   ├── memory/
│   │   ├── session_manager.py       # Sessions via mempalace
│   │   ├── event_store.py           # Events via mempalace KG
│   │   ├── memory_engine.py         # Conflict resolution via mempalace
│   │   ├── rollback_manager.py      # Rollback via mempalace drawers
│   │   └── skills_manager.py        # Skills via mempalace
│   ├── indexing/
│   │   ├── code_indexer.py          # AST indexer via mempalace
│   │   └── entity_tracker.py        # Entity tracking via mempalace KG
│   ├── workflow/                    # V2: Checkpoints
│   ├── vision/                      # FastVLM server
│   ├── llm/                         # Model router (Ollama)
│   ├── communication/               # Retry/circuit breaker
│   ├── performance/                 # psutil monitor
│   └── toon/                        # Token budget
│
├── mcps/                            # 5 MCPs especializados
│   ├── architect_mcp.py
│   ├── backend_developer_mcp.py
│   ├── frontend_developer_mcp.py
│   ├── tester_mcp.py
│   └── vision_specialist_mcp_optional.py
│
├── config/toon/                     # TOONs por rol
├── fastvlm-webgpu/                  # Vision client (browser)
├── tests/                           # V2 integration + unit tests
└── docs/
```

---

## Tools (25+)

### Core
- `ping`, `get_context`, `validate_response`, `index_status`

### Sessions
- `create_session`, `list_sessions`, `get_session_summary`, `delete_session`

### Code Intelligence
- `index_code`, `search_entity`, `extended_index`, `extended_search`

### Memory & Skills
- `memory_tool`, `skills_tool`, `get_knowledge_summary`

### JEPA & Grounding
- `audit_jepa`, `sync_world_model`, `ground_project_context`

### Code Guardian
- `check_code_creation`, `analyze_project_redundancy`, `get_code_suggestions`, `learn_from_context`

### Advanced
- `process_advanced`, `expand_query`, `chunk_document`, `add_feedback`, `optimize_configuration`

### System
- `get_system_status`, `get_smart_status`

---

## Memory Gateway (7 tools)

- `gateway_status` — Estado del gateway
- `gateway_set_active_feature` — Define feature activa
- `gateway_add_adr` — Registra ADR
- `gateway_add_knowledge` — Conocimiento estable
- `gateway_add_task` — Tareas de desarrollo
- `gateway_compress_session` — Comprime sesion
- `gateway_build_context` — Context builder (prompt compacto)

---

## Flujo V2 con Checkpoints

```
Usuario -> [requirements.md] -> OrchestratorV2
  |
MarkdownReader -> parse requerimientos
  |
ChecklistManager -> crea tareas
  |
Tarea 1: ArchitectMCP -> checkpoint -> user APPROVE
Tarea 2: BackendDeveloperMCP -> checkpoint -> user APPROVE
Tarea 3: FrontendDeveloperMCP -> checkpoint -> user APPROVE
Tarea 4: TesterMCP -> checkpoint -> user APPROVE
```

---

## Instalacion

```bash
pip install -r requirements.txt
playwright install chromium
```

**Dependencias clave:**
- `mempalace>=3.0.0` — Backend unificado (ChromaDB + SQLite KG)
- `mcp>=0.3.0` — MCP protocol
- `structlog>=23.1.0` — Structured logging
- `aiohttp>=3.14.0` — Async HTTP
- `tiktoken>=0.5.0` — Token counting
- `pydantic>=2.0.0` — Data validation

**Eliminados en V11:**
- `torch` (~4GB)
- `sentence-transformers`
- `hnswlib`
- `pymp4`

---

## Branches

- `v11-mempalace` — Desarrollo con mempalace backend
- `main` — Estable (V10 + Code Guardian + V2 workflow)
- `origin/feature/code-guardian-mcp-integration` — Ya mergeado en main

---

## Documentacion

- [V8 User Guide](docs/V8_USER_GUIDE.md)
- [V8 Technical](docs/V8_TECHNICAL_DOCUMENTATION.md)
- [HUB V2 Workflow](IMPLEMENTACION_FLUJO_CORRECTO.md)
- [Anti-Alucinacion](V9_ANTI_ALUCINACION_ANALISIS.md)

---

**Version**: V11.0.0 (Mempalace Backend)
**Fecha**: 2026-06-03
