# PLAN: Eliminación V2 + Integración Superpowers
**Status:** EN PROGRESO
**Fecha:** 2026-06-03
**Rama:** v11-mempalace

---

## Objetivo
Eliminar la capa V2 redundante y usar superpowers como orquestador de workflow.
Mantener MCPs como tools layer sin redundancia.

---

## Fase 1: Análisis de Redundancia (COMPLETADA)

### V2 vs Superpowers - Mapeo Completo

**core/ - Workflow y Memoria:**
| Capa V2 | Superpowers Equivalente | Acción |
|---------|------------------------|--------|
| `workflow/checklist_manager.py` | `todowrite` + `executing-plans` | ELIMINAR |
| `workflow/checkpoint_handler.py` | `verification-before-completion` | ELIMINAR |
| `workflow/markdown_reader.py` | `read` tool nativo | ELIMINAR |
| `memory/session_manager.py` | `using-git-worktrees` | ELIMINAR |
| `memory/skills_manager.py` | skill system superpowers | ELIMINAR |
| `memory/event_store.py` | mempalace drawers | ELIMINAR |
| `memory/memory_engine.py` | mempalace backend | ELIMINAR |
| `memory/rollback_manager.py` | git nativo | ELIMINAR |
| `memory/summarizing_session.py` | compactación sesiones | ELIMINAR |
| `memory/trimming_session.py` | compactación sesiones | ELIMINAR |
| `resolution/contextual_resolver.py` | `explore` agent | ELIMINAR |
| `resolution/reference_detector.py` | `explore` agent + grep | ELIMINAR |
| `indexing/code_indexer.py` | mempalace kg | ELIMINAR |
| `indexing/entity_tracker.py` | mempalace kg | ELIMINAR |
| `communication/circuit_breaker.py` | `systematic-debugging` | ELIMINAR |
| `communication/protocol.py` | MCP protocol nativo | ELIMINAR |
| `extended_knowledge.py` | mempalace drawers | ELIMINAR |
| `smart_session_orchestrator.py` | `executing-plans` | ELIMINAR |
| `advanced_features/orchestrator.py` | `subagent-driven-development` | ELIMINAR |

**mcps/ - MCPs Especializados:**
| Archivo | Superpowers Equivalente | Acción |
|---------|------------------------|--------|
| `mcps/architect_mcp.py` | `brainstorming` + `writing-plans` | ELIMINAR |
| `mcps/backend_developer_mcp.py` | `executing-plans` + TDD | ELIMINAR |
| `mcps/frontend_developer_mcp.py` | `executing-plans` + TDD | ELIMINAR |
| `mcps/developer_mcp.py` | `executing-plans` | ELIMINAR |
| `mcps/tester_mcp.py` | `verification-before-completion` | ELIMINAR |
| `mcps/vision_specialist_mcp.py` | MCP vision nativo | ELIMINAR |
| `mcps/vision_specialist_mcp_optional.py` | MCP vision nativo | ELIMINAR |
| `mcps/base_mcp.py` | No necesario | ELIMINAR |

**mcps/contracts/ - Contratos Pydantic:**
| Archivo | Equivalente | Acción |
|---------|-------------|--------|
| `contracts/architect_contracts.py` | Skills definen I/O | ELIMINAR |
| `contracts/backend_developer_contracts.py` | Skills definen I/O | ELIMINAR |
| `contracts/frontend_developer_contracts.py` | Skills definen I/O | ELIMINAR |
| `contracts/developer_contracts.py` | Skills definen I/O | ELIMINAR |
| `contracts/tester_contracts.py` | Skills definen I/O | ELIMINAR |

**config/toon/ - Archivos TOON:**
| Archivo | Superpowers Equivalente | Acción |
|---------|------------------------|--------|
| `toon/architect.toon` | `brainstorming` skill | ELIMINAR |
| `toon/backend_developer.toon` | `executing-plans` skill | ELIMINAR |
| `toon/frontend_developer.toon` | `executing-plans` skill | ELIMINAR |
| `toon/developer.toon` | `executing-plans` skill | ELIMINAR |
| `toon/tester.toon` | `verification-before-completion` skill | ELIMINAR |
| `toon/orchestrator.toon` | `subagent-driven-development` skill | ELIMINAR |
| `toon/global_rules.toon` | Superpowers globales | ELIMINAR |

**tests/ - Tests V2:**
| Archivo | Acción |
|---------|--------|
| `tests/integration/test_workflow_simple.py` | ELIMINAR |
| `tests/integration/test_workflow_with_checkpoints.py` | ELIMINAR |
| `tests/unit/test_circuit_breaker.py` | ELIMINAR |
| `tests/unit/test_event_store.py` | ELIMINAR |
| `tests/unit/test_memory_engine.py` | ELIMINAR |
| `tests/unit/test_protocol.py` | ELIMINAR |

**data/ - Datos V2:**
| Archivo | Acción |
|---------|--------|
| `data/smart_sessions/` | ELIMINAR |
| `core/data/smart_sessions/` | ELIMINAR |

---

## Fase 2: Arquitectura Resultante

### Skills Layer (workflow)
```
brainstorming → writing-plans → subagent-driven-development
     ↓               ↓                    ↓
 explore agent   mempalace          parallel agents
     ↓               ↓                    ↓
verification-before-completion
     ↓
receiving-code-review → finishing-a-development-branch
```

### MCPs Layer (tools)
```
mempalace: almacenamiento + knowledge graph
mcp-hub: orquestación de tools
filesystem: archivos del proyecto
github: repo, PRs, issues
```

### Flujo de Desarrollo
```
1. Usuario pide feature/bug
2. brainstorming → diseña (reemplaza architect role)
3. writing-plans → crea plan con micro-tareas TDD
4. subagent-driven-development → dispatcha agentes por tarea
   - Cada agente: TDD (test → fail → implement → pass → commit)
5. agente principal → verification-before-completion
6. finishing-a-development-branch → merge/PR
```

---

## Fase 3: Eliminación de Archivos

### Archivos a ELIMINAR:

**Directorios completos:**
```
core/workflow/                    (3 archivos)
core/memory/                      (7 archivos)
core/resolution/                  (2 archivos)
core/indexing/                     (2 archivos)
core/communication/               (2 archivos)
mcps/                             (8+5 archivos, directorio completo)
config/toon/                      (7 archivos, directorio completo)
core/data/smart_sessions/         (datos)
data/smart_sessions/              (datos)
```

**Archivos sueltos:**
```
core/extended_knowledge.py
core/smart_session_orchestrator.py
core/advanced_features/orchestrator.py
```

**Tests V2:**
```
tests/integration/test_workflow_simple.py
tests/integration/test_workflow_with_checkpoints.py
tests/unit/test_circuit_breaker.py
tests/unit/test_event_store.py
tests/unit/test_memory_engine.py
tests/unit/test_protocol.py
```

**Total: ~50 archivos a eliminar**

### Archivos a MANTENER:
```
core/v6.py                        (simplificado - quitar imports V2)
core/mcp_http_server.py           (transport layer, 43 tools)
core/mcp_stdio.py                 (stdio entry point)
core/mempalace_backend.py         (bridge a mempalace)
core/storage/                     (lógica custom sobre mempalace)
core/pretty_logger.py             (logging)
core/log_config.py                (logging config)
core/nvidia_proxy.py              (proxy NVIDIA)
core/llm/                         (LLM integration)
core/vision/                      (vision)
core/performance/                 (performance)
core/__init__.py                  (actualizar imports)
```

**Tests a MANTENER:**
```
tests/test_mcp_connection.py
tests/test_v6_only.py
tests/test_verbose.py
tests/test_verbose_fixed.py
tests/test_verbose_simple.py
tests/unit/status.py
tests/unit/test_integration_v6.py
tests/unit/test_mcp_server.py
tests/unit/test_multi_agent.py
tests/unit/test_v6_storage.py
tests/unit/test_vision_hub.py
```

---

## Fase 4: Limpieza de Rama

### Pre-requisitos:
1. Verificar que no hay imports rotos en v6.py
2. Verificar que mcp_http_server.py no depende de archivos eliminados
3. Verificar que mempalace_backend.py no depende de archivos eliminados
4. Test: el MCP server levanta correctamente

### Pasos:
1. Eliminar archivos V2 (directorios + sueltos + tests)
2. Actualizar imports en v6.py (quitar referencias V2)
3. Actualizar core/__init__.py
4. Test local: MCP server levanta
5. Test local: todas las tools responden
6. Commit: `refactor: remove V2 workflow layer, superpowers as orchestrator`
7. Force push a v11-mempalace (limpiar historial si necesario)
8. Verificar que remote está limpio

---

## Fase 5: Verificación

### Checklist:
- [ ] MCP server levanta sin errores
- [ ] Todas las 43 tools responden
- [ ] mempalace funciona (add_drawer, search, kg_add)
- [ ] No hay imports de archivos eliminados
- [ ] Tests V2 eliminados
- [ ] Tests existentes pasan
- [ ] Rama remote limpia (sin commits viejos)

---

## Decisiones Tomadas
1. Superpowers ES el orquestador de workflow
2. MCPs SON las tools, no workflow
3. No hay redundancia skills ↔ MCPs (son capas diferentes)
4. writing-plans + subagent-driven-development = flujo completo
5. agente principal verifica con verification-before-completion
6. TOON files eliminados (skills los reemplazan)
7. Contratos Pydantic eliminados (skills definen I/O)
8. MCPs especializados eliminados (unified server los reemplaza)

---

## Notas
- El proxy NVIDIA se mantiene como fallback
- MCP configs no cambian (siguen apuntando a mcp_stdio.py)
- Solo se elimina código Python V2 redundante
- ~50 archivos a eliminar
- v6.py se simplifica (quitar imports V2)
