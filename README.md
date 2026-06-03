# 🌀 MCP HUB V12 — Unified Context Vortex & Memory Gateway

> **El servidor MCP centralizado definitivo. Un solo punto de entrada (`mcp_stdio.py`) que proporciona más de 40 herramientas para Inteligencia Contextual, Code Guardian, Vision, y Memory Gateway respaldado por MemPalace.**

---

## 🏗️ Arquitectura Unificada (Agnóstica)

El HUB V12 consolida todas las características en un único servidor MCP agnóstico compatible con cualquier cliente (OpenCode, Claude Code, Gemini CLI, Cursor, etc.). Utiliza transporte estándar `stdio` garantizando una comunicación JSON-RPC estable sin interferencias visuales.

### 📊 Diagrama de Arquitectura

![Diagrama Arquitectura V12](diagrama.png)

---

## 🔄 Flujo de Datos y Ciclo de Vida de la Información

El ciclo de vida de los datos está diseñado para maximizar el rendimiento del LLM minimizando el consumo de tokens mediante compresión y recuperación contextual:

1. **Ingesta (Input):**
   - El agente ejecuta herramientas como `gateway_add_task` o `gateway_add_adr`.
   - Code Guardian indexa código automáticamente (`index_code`).
2. **Persistencia (Storage):**
   - Los datos se almacenan en las "Rooms" de MemPalace.
   - Las relaciones complejas y fragmentos de texto son administrados directamente por el motor unificado de MemPalace, eliminando la necesidad de bases de datos externas fragmentadas o dependencias pesadas como `torch`.
3. **Compresión (Lifecycle Management):**
   - El historial temporal (`/context`) y las sesiones se comprimen incrementalmente mediante `gateway_compress_session` hacia la room `/summaries`.
4. **Recuperación (Output):**
   - En cada iteración de desarrollo, el agente llama a `gateway_build_context`.
   - Esta herramienta recupera tareas activas, el stack del proyecto (`/knowledge`), las decisiones de arquitectura (`/decisions`) y los resúmenes recientes.
   - **Resultado:** En lugar de inyectar 20,000 tokens de historial de chat, el LLM recibe un super-prompt compilado de apenas ~200 tokens con el contexto exacto.

---

## 🛠️ Herramientas Disponibles (43 Tools Unificadas)

El HUB expone un arsenal completo de herramientas agrupadas por capacidad para brindar autonomía total a los agentes:

### 🌐 V12 Memory Gateway (MemPalace)
Gestiona la persistencia a largo plazo y el conocimiento del proyecto:
- `gateway_status`: Obtiene el estado actual de la memoria y la feature activa.
- `gateway_set_active_feature`: Cambia el foco del agente hacia una rama/feature específica.
- `gateway_add_adr`: Añade un Architectural Decision Record (ADR) para documentar decisiones clave.
- `gateway_add_knowledge`: Añade reglas, convenciones o conocimiento estable del stack del proyecto.
- `gateway_add_task`: Registra una nueva tarea en el backlog (estados: todo, in_progress, done).
- `gateway_compress_session`: Analiza y comprime el historial reciente para reducir consumo de tokens.
- `gateway_build_context`: **Herramienta Estrella.** Compila un super-prompt ultracompacto (ADRs, conocimiento, y tareas activas) para inyectar al LLM al iniciar un agente.

### 🛡️ Code Guardian
Prevención de errores y análisis de calidad antes de escribir código:
- `check_code_creation`: Realiza validaciones estáticas y previene malas prácticas antes de la modificación.
- `analyze_project_redundancy`: Escanea el repositorio para evitar reescribir utilidades que ya existen.
- `get_code_suggestions`: Revisa fragmentos y sugiere mejoras de optimización.
- `learn_from_context`: Analiza el estilo del proyecto para adaptar futuras generaciones de código.

### 🌀 Context Vortex & Indexing (Code Intel)
Herramientas de recuperación y entendimiento semántico del código:
- `index_code`: Fuerza la indexación AST de un directorio o archivo específico al motor unificado.
- `search_entity`: Busca clases, funciones o variables exactas dentro de la base de código.
- `extended_index` / `extended_search`: Búsqueda profunda en documentaciones, constantes y patrones.
- `get_knowledge_summary`: Extrae un mapa mental de la estructura actual del proyecto.

### 🧠 Smart Sessions & Orchestration
Herramientas para mantener el enfoque de agentes múltiples:
- `create_session` / `delete_session` / `list_sessions`: Gestión del ciclo de vida de conversaciones.
- `get_session_summary`: Recupera un resumen narrativo de qué se hizo en sesiones anteriores.
- `smart_session_init` / `smart_query`: Motor iterativo de preguntas/respuestas respaldado por MemPalace.
- `get_smart_status` / `get_system_status`: Verificación de salud del HUB y sus subsistemas.

### 🌍 World Model & Quality (JEPA)
Validación factual anti-alucinaciones:
- `sync_world_model`: Sincroniza el estado actual de los archivos clave con la memoria interna.
- `audit_jepa`: Evalúa una propuesta de código del LLM cruzándola contra el modelo del mundo del proyecto para detectar alucinaciones.
- `check_quality` / `get_quality_principles`: Verificación de QA y reglas estables.

### ⚙️ Herramientas Base (V5 Core)
- `ping`: Verificación de latencia y conectividad del MCP.
- `get_context`: Búsqueda de vectores en crudo sobre MemPalace.
- `validate_response`: Herramienta interna de auto-evaluación.
- `index_status`: Comprueba cuántos archivos/tokens están indexados actualmente.

### 🌐 Herramientas Específicas de Framework (Django/FE)
- `escanear_urls_django`: Encuentra e indexa rutas de un proyecto Django automáticamente.
- `analizar_tokens_css`: Extrae variables y clases utilitarias de CSS/Tailwind.

### 👁️ Vision Specialist
- Toma asíncrona de screenshots a través de Playwright y análisis de interfaz usando FastVLM (Lazy-loaded para velocidad extrema de inicio del MCP).

---

## 🚀 Inicio Rápido y Configuración

No es necesario arrancar el servidor manualmente. El cliente MCP (ej. OpenCode) lo inicializa automáticamente cuando es requerido a través de stdio.

### Requisitos
```bash
pip install -r requirements.txt
playwright install chromium
```

### Configuración en Clientes
El HUB debe registrarse en tu cliente apuntando a `mcp_stdio.py`. 

Ejemplo para `opencode.json`:
```json
"memory-gateway": {
    "command": [
        "python",
        "\\HUB\\core\\mcp_stdio.py"
    ],
    "type": "local",
    "enabled": true
}
```

---

## 🧹 Estructura del Proyecto

Se ha eliminado el código redundante y mantenido una arquitectura ultra-limpia:

```text
HUB/
├── core/
│   ├── mcp_stdio.py                 # 🌟 PUNTO DE ENTRADA ÚNICO (Transporte Stdio)
│   ├── mcp_http_server.py           # Engine Principal (FastMCP) y lógica de herramientas
│   ├── mempalace_backend.py         # Conector unificado de MemPalace
│   ├── visual_monitor.py            # Monitor Visual (Apagado preventivamente en stdio)
│   ├── pretty_logger.py             # Logging seguro para consolas (evita corrupción JSON-RPC)
│   ├── advanced_features/           # Componentes de Code Guardian y Vortex
│   ├── vision/                      # Módulo de procesamiento visual
│   ├── memory/                      # Gestión de estados y contexto
│   └── storage/                     # Wrappers de persistencia
├── data/                            # Almacenamiento local de la memoria (ignorado en git)
├── logs/                            # Registros de ejecución
└── tests/                           # Suite de 17 tests unitarios y de integración (100% passing)
```

---
**Versión**: V12.0.0 (Unified Architecture)  
**Estado**: Estable, Unit Tests 100% Passed.
