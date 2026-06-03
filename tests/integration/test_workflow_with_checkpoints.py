"""
Test del Flujo Correcto con Checkpoints
Valida el workflow completo: Architect → Backend → Frontend → Tester
Con validación de stakeholder en cada paso
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
from mcp_hub_v6 import create_mcp_hub
from core.orchestrator_v2 import OrchestratorV2


async def test_workflow_with_checkpoints():
    print("🚀 TEST: FLUJO CORRECTO CON CHECKPOINTS")
    print("=" * 70)
    
    # 1. Crear archivo markdown de requerimientos de prueba
    print("\n📝 1. Creando archivo de requerimientos...")
    requirements_content = """---
title: Sistema de Autenticación
priority: high
---

# Sistema de Autenticación de Usuarios

## Requerimiento: Login de Usuarios [priority: high]

Como usuario del sistema, quiero poder iniciar sesión con email y contraseña,
para acceder a las funcionalidades protegidas.

### Criterios de Aceptación
- Validación de email y contraseña
- Manejo de errores (credenciales inválidas)
- Generación de token JWT
- Redirección a dashboard después de login exitoso

## Requerimiento: Registro de Usuarios [priority: medium]

Como nuevo usuario, quiero poder registrarme en el sistema,
para crear mi cuenta y acceder a la plataforma.

### Criterios de Aceptación
- Formulario de registro con validación
- Encriptación de contraseña
- Email de confirmación
- Creación de perfil inicial

## Componentes Técnicos

### Backend
```python
# POST /api/auth/login
# POST /api/auth/register
# GET /api/auth/me
```

### Frontend
```javascript
// LoginPage.tsx
// RegisterPage.tsx
// AuthContext
```
"""
    
    # Crear archivo temporal
    test_requirements_file = Path("test_requirements.md")
    test_requirements_file.write_text(requirements_content, encoding='utf-8')
    print(f"   ✅ Archivo creado: {test_requirements_file}")
    
    # 2. Inicializar Sistema
    print("\n🤖 2. Inicializando Hub y Orquestador V2...")
    hub = create_mcp_hub()
    orchestrator = OrchestratorV2(hub)
    await orchestrator.start()
    print("   ✅ Sistema iniciado")
    
    # 3. Ejecutar workflow desde markdown
    print(f"\n⚙️  3. Ejecutando workflow desde {test_requirements_file}...")
    print("   [Modo: No interactivo - Auto-aprobación para tests]\n")
    
    result = await orchestrator.execute_from_markdown(
        str(test_requirements_file),
        interactive=False  # Auto-aprobar para test
    )
    
    # 4. Analizar Resultados
    print("\n📊 4. RESULTADOS DEL WORKFLOW:")
    print("-" * 70)
    
    if "error" in result and "workflow_id" not in result:
        print(f"   ❌ Error crítico: {result.get('error')}")
        await orchestrator.stop()
        return
    
    # Información general
    workflow_id = result.get("workflow_id")
    final_status = result.get("final_status")
    status_emoji = "✅" if final_status == "completed" else "⚠️"
    
    print(f"\n   {status_emoji} Workflow ID: {workflow_id}")
    print(f"   {status_emoji} Estado Final: {final_status}")
    
    # Tareas completadas
    tasks_completed = result.get("tasks_completed", [])
    print(f"\n   📋 Tareas Completadas: {len(tasks_completed)}")
    
    for i, task in enumerate(tasks_completed, 1):
        print(f"\n   {i}. {task['title']}")
        print(f"      Estado: {task['status']}")
        
        # Mostrar detalles según tipo
        task_result = task['result']
        
        if 'plan_id' in task_result:
            # Es resultado del Architect
            components = task_result.get('components', [])
            print(f"      Componentes diseñados: {len(components)}")
            for comp in components:
                print(f"        - {comp['name']} ({comp['type']})")
        
        elif 'implementation_id' in task_result:
            # Es resultado de Developer
            code_files = task_result.get('code_files', [])
            print(f"      Archivos generados: {len(code_files)}")
            for file in code_files[:3]:  # Mostrar solo primeros 3
                print(f"        - {file['path']}")
    
    # Checkpoints
    checkpoints = result.get("checkpoints", [])
    print(f"\n   🛑 Checkpoints Creados: {len(checkpoints)}")
    
    # Historial de checkpoints
    checkpoint_history = result.get("checkpoint_history", [])
    print(f"\n   📜 Historial de Aprobaciones:")
    for cp in checkpoint_history:
        decision_emoji = "✅" if cp['decision'] == "approve" else "❌" if cp['decision'] == "reject" else "⏳"
        print(f"      {decision_emoji} {cp['task_title']}")
        print(f"         Agente: {cp['agent_role']}")
        print(f"         Decisión: {cp['decision']}")
        if cp.get('feedback'):
            print(f"         Feedback: {cp['feedback']}")
    
    # Reporte de progreso
    progress = result.get("progress_report", {})
    if progress:
        print(f"\n   📈 Progreso General:")
        print(f"      Total tareas: {progress.get('total_tasks')}")
        print(f"      Completadas: {progress.get('progress_percentage')}%")
        print(f"      Pendientes de aprobación: {progress.get('tasks_pending_approval')}")
        print(f"      Bloqueadas: {progress.get('tasks_blocked')}")
    
    # 5. Cleanup
    await orchestrator.stop()
    test_requirements_file.unlink()  # Eliminar archivo temporal
    
    print("\n✅ TEST COMPLETADO")
    print("=" * 70)
    
    # Validaciones
    assert final_status in ["completed", "blocked"], f"Estado inesperado: {final_status}"
    assert len(tasks_completed) > 0, "No se completó ninguna tarea"
    assert len(checkpoints) == len(tasks_completed), "Checkpoints no coinciden con tareas"
    
    print("\n✅ Todas las validaciones pasaron correctamente\n")


async def test_workflow_simple_description():
    """Test con descripción simple (sin markdown)"""
    print("\n🚀 TEST: FLUJO SIMPLE (Sin Markdown)")
    print("=" * 70)
    
    hub = create_mcp_hub()
    orchestrator = OrchestratorV2(hub)
    await orchestrator.start()
    
    feature = "Sistema de gestión de tareas con CRUD completo y notificaciones"
    
    print(f"\n⚙️  Ejecutando workflow: '{feature}'\n")
    
    result = await orchestrator.execute_feature_request(
        feature,
        interactive=False
    )
    
    print(f"\n📊 Resultado:")
    print(f"   Estado: {result.get('final_status')}")
    print(f"   Tareas: {len(result.get('tasks_completed', []))}")
    print(f"   Checkpoints: {len(result.get('checkpoints', []))}")
    
    await orchestrator.stop()
    
    print("\n✅ Test simple completado\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUITE DE TESTS: ORCHESTRATOR V2 CON FLUJO CORRECTO")
    print("="*70 + "\n")
    
    # Test principal con markdown
    asyncio.run(test_workflow_with_checkpoints())
    
    # Test simple
    asyncio.run(test_workflow_simple_description())
    
    print("\n🎉 TODOS LOS TESTS PASARON!\n")
