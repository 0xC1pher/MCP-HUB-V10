# ESTADO ACTUAL: Flujo de Desarrollo V2 → Superpowers

**Fecha original**: 2025-12-02
**Fecha de actualización**: 2026-06-03
**Status**: EN TRANSICIÓN - V2 a eliminir, Superpowers como orquestador

---

## Resumen

El sistema V2 implementó un flujo de desarrollo con roles especializados (architect, backend, frontend, tester), checkpoints, y orquestación custom. Todo eso fue **consolidado** en el MCP server unificado (43 tools) y ahora se **elimina** porque superpowers ya cubre el workflow completo.

---

## Estado Actual de los Archivos V2

### mcps/ - MCPs Especializados (OBSOLETOS)

| Archivo | Estado | Equivalente Superpowers |
|---------|--------|------------------------|
| `architect_mcp.py` | ❌ OBSTOLETO | `brainstorming` + `writing-plans` |
| `backend_developer_mcp.py` | ❌ OBSTOLETO | `executing-plans` + `test-driven-development` |
| `frontend_developer_mcp.py` | ❌ OBSTOLETO | `executing-plans` + `test-driven-development` |
| `tester_mcp.py` | ❌ OBSTOLETO | `verification-before-completion` |
| `developer_mcp.py` | ❌ OBSTOLETO | `executing-plans` |
| `vision_specialist_mcp.py` | ❌ OBSTOLETO | MCP vision nativo |
| `vision_specialist_mcp_optional.py` | ❌ OBSTOLETO | MCP vision nativo |
| `base_mcp.py` | ❌ OBSTOLETO | No necesario |

### mcps/contracts/ - Contratos Pydantic (OBSOLETOS)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `architect_contracts.py` | ❌ OBSTOLETO | Skills definen I/O |
| `backend_developer_contracts.py` | ❌ OBSTOLETO | Skills definen I/O |
| `frontend_developer_contracts.py` | ❌ OBSTOLETO | Skills definen I/O |
| `developer_contracts.py` | ❌ OBSTOLETO | Skills definen I/O |
| `tester_contracts.py` | ❌ OBSTOLETO | Skills definen I/O |

### config/toon/ - Archivos TOON por Rol (OBSOLETOS)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `architect.toon` | ❌ OBSTOLETO | `brainstorming` skill |
| `backend_developer.toon` | ❌ OBSTOLETO | `executing-plans` skill |
| `frontend_developer.toon` | ❌ OBSTOLETO | `executing-plans` skill |
| `developer.toon` | ❌ OBSTOLETO | `executing-plans` skill |
| `tester.toon` | ❌ OBSTOLETO | `verification-before-completion` skill |
| `orchestrator.toon` | ❌ OBSTOLETO | `subagent-driven-development` skill |
| `global_rules.toon` | ❌ OBSTOLETO | Superpowers globales |

### core/workflow/ - Sistema de Workflow (OBSOLETO)

| Archivo | Estado | Equivalente Superpowers |
|---------|--------|------------------------|
| `checklist_manager.py` | ❌ OBSTOLETO | `todowrite` (tracking nativo) |
| `checkpoint_handler.py` | ❌ OBSTOLETO | `verification-before-completion` |
| `markdown_reader.py` | ❌ OBSTOLETO | `read` tool nativo |

### core/memory/ - Sistema de Memoria V2 (OBSOLETO)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `session_manager.py` | ❌ OBSTOLETO | `using-git-worktrees` + sesiones |
| `skills_manager.py` | ❌ OBSTOLETO | skill system superpowers |
| `event_store.py` | ❌ OBSTOLETO | mempalace drawers |
| `memory_engine.py` | ❌ OBSTOLETO | mempalace backend |
| `rollback_manager.py` | ❌ OBSTOLETO | git nativo |
| `summarizing_session.py` | ❌ OBSTOLETO | compactación sesiones |
| `trimming_session.py` | ❌ OBSTOLETO | compactación sesiones |

### core/resolution/ - Resolución de Contexto (OBSOLETO)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `contextual_resolver.py` | ❌ OBSTOLETO | `explore` agent |
| `reference_detector.py` | ❌ OBSTOLETO | `explore` agent + grep |

### core/indexing/ - Indexación (OBSOLETO)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `code_indexer.py` | ❌ OBSTOLETO | mempalace knowledge graph |
| `entity_tracker.py` | ❌ OBSTOLETO | mempalace kg_add/kg_query |

### core/communication/ - Comunicación (OBSOLETO)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `circuit_breaker.py` | ❌ OBSTOLETO | `systematic-debugging` |
| `protocol.py` | ❌ OBSTOLETO | MCP protocol nativo |

### Otros Archivos V2 (OBSOLETOS)

| Archivo | Estado | Equivalente |
|---------|--------|-------------|
| `core/extended_knowledge.py` | ❌ OBSTOLETO | mempalace drawers |
| `core/smart_session_orchestrator.py` | ❌ OBSTOLETO | `executing-plans` |
| `core/advanced_features/orchestrator.py` | ❌ OBSTOLETO | `subagent-driven-development` |
| `core/data/smart_sessions/` | ❌ OBSTOLETO | mempalace |
| `data/smart_sessions/` | ❌ OBSTOLETO | mempalace |

### Tests V2 (OBSOLETOS)

| Archivo | Estado |
|---------|--------|
| `tests/integration/test_workflow_simple.py` | ❌ OBSTOLETO |
| `tests/integration/test_workflow_with_checkpoints.py` | ❌ OBSTOLETO |
| `tests/unit/test_circuit_breaker.py` | ❌ OBSTOLETO |
| `tests/unit/test_event_store.py` | ❌ OBSTOLETO |
| `tests/unit/test_memory_engine.py` | ❌ OBSTOLETO |
| `tests/unit/test_protocol.py` | ❌ OBSTOLETO |

---

## Archivos que SE MANTIENEN (Infraestructura MCP)

### core/ - MCP Server
| Archivo | Función |
|---------|---------|
| `v6.py` | MCP server + tool definitions (simplificado) |
| `mcp_http_server.py` | Transport HTTP/SSE (43 tools unificadas) |
| `mcp_stdio.py` | Transport stdio para MCP configs |
| `mempalace_backend.py` | Bridge a mempalace |
| `storage/` | Lógica custom sobre mempalace |
| `pretty_logger.py` | Logging |
| `log_config.py` | Config de logging |
| `nvidia_proxy.py` | Proxy NVIDIA NIM |

### mcps/ - Solo si se mantiene algo
| Archivo | Función |
|---------|---------|
| `__init__.py` | Imports (actualizar) |

---

## Nueva Arquitectura de Flujo

```
┌─────────────────────────────────────────────────┐
│              SKILLS (workflow layer)             │
│                                                 │
│  brainstorming → writing-plans → subagent-dev   │
│       ↓              ↓              ↓           │
│  explore agent   mempalace    parallel agents   │
│                                                 │
│  verification-before-completion                 │
│       ↓                                         │
│  receiving-code-review → finishing-a-branch     │
└──────────────────────┬──────────────────────────┘
                       │ usa
                       ▼
┌─────────────────────────────────────────────────┐
│              MCPs (tools layer)                  │
│                                                 │
│  mempalace: almacenamiento + knowledge graph    │
│  mcp-hub: orquestación de tools                 │
│  filesystem: archivos del proyecto              │
│  github: repo, PRs, issues                      │
└─────────────────────────────────────────────────┘
```

### Flujo de Desarrollo (NUEVO)

```
1. Usuario pide feature/bug
2. brainstorming → diseña (reemplaza architect role)
3. writing-plans → crea plan con micro-tareas TDD
4. subagent-driven-development → dispatcha agentes por tarea
   - Cada agente: TDD (test → fail → implement → pass → commit)
5. agente principal → verification-before-completion
6. finishing-a-development-branch → merge/PR
```

### Comparación: V2 vs Superpowers

| Función V2 | Superpowers | Mejora |
|------------|-------------|--------|
| Architect role | `brainstorming` skill | Más disciplinado, hard-gates |
| ChecklistManager | `todowrite` | Nativo, sin código custom |
| CheckpointHandler | `verification-before-completion` | Integrado con workflow |
| OrchestratorV2 | `subagent-driven-development` | Paralelismo real |
| RollbackManager | git nativo | Más robusto |
| SessionManager | `using-git-worktrees` | Aislamiento real |
| SkillsManager | skill system | Más flexible |
| CircuitBreaker | `systematic-debugging` | Root cause analysis |
| CommunicationProtocol | MCP protocol nativo | Estándar |

---

## Plan de Eliminación

**Ver:** `PLAN_eliminacion_v2.md` para detalles completos.

### Resumen de Eliminación

**Eliminar (18+ archivos):**
- `mcps/` completo (8 MCPs especializados)
- `mcps/contracts/` completo (5 contratos)
- `config/toon/` completo (7 TOON files)
- `core/workflow/` completo (3 archivos)
- `core/memory/` completo (7 archivos)
- `core/resolution/` completo (2 archivos)
- `core/indexing/` completo (2 archivos)
- `core/communication/` completo (2 archivos)
- `core/extended_knowledge.py`
- `core/smart_session_orchestrator.py`
- `core/advanced_features/orchestrator.py`
- `core/data/smart_sessions/`
- `data/smart_sessions/`
- Tests V2 (6 archivos)

**Mantener:**
- `core/v6.py` (simplificado)
- `core/mcp_http_server.py`
- `core/mcp_stdio.py`
- `core/mempalace_backend.py`
- `core/storage/`
- `core/pretty_logger.py`
- `core/log_config.py`
- `core/nvidia_proxy.py`

---

## Workshops Activos

| Workshop | Archivo | Status |
|----------|---------|--------|
| Eliminación V2 | `PLAN_eliminacion_v2.md` | EN PROGRESO |
| claw-code NVIDIA | `WORKSHOP_clawcode_nvidia.md` | PLANNED |

---

## MCPs Actualmente en Uso

**OpenCode** usa el MCP unificado:
```
memory-gateway → HUB/core/mcp_stdio.py (43 tools)
mempalace → mempalace.mcp_server directo
filesystem → @modelcontextprotocol/server-filesystem
github → ghcr.io/github/github-mcp-server
railway → railway mcp
```

**NO** se usan los MCPs especializados de V2 (están obsoletos).

---

**Status**: EN TRANSICIÓN
**Última actualización**: 2026-06-03
**Próximo paso**: Ejecutar eliminación V2
