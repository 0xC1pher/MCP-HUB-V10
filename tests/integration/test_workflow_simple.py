"""
Test Simplificado del Flujo V2
Sin dependencias de Vision ni componentes pesados
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import asyncio
from datetime import datetime


# Test manual sin dependencias externas
async def test_workflow_components():
    """Test de componentes individuales del workflow"""
    print("\n🧪 TEST: COMPONENTES DEL WORKFLOW V2")
    print("=" * 70)
    
    # 1. Test MarkdownReader
    print("\n1️⃣  Test: MarkdownReader")
    from core.workflow.markdown_reader import MarkdownReader, MarkdownRequirement
    
    reader = MarkdownReader()
    
    # Crear archivo de prueba
    test_md = Path("test_req_simple.md")
    test_md.write_text("""# Mi Proyecto

## Requerimiento: Feature 1

Descripción del feature 1

## Requerimiento: Feature 2  

Descripción del feature 2
""", encoding='utf-8')
    
    data = reader.read_file(str(test_md))
    print(f"   ✅ Secciones encontradas: {len(data['sections'])}")
    print(f"   ✅ Requerimientos: {len(data['requirements'])}")
    
    test_md.unlink()  # Limpiar
    
    # 2. Test ChecklistManager
    print("\n2️⃣  Test: ChecklistManager")
    from core.workflow.checklist_manager import ChecklistManager, TaskPriority, TaskStatus
    
    checklist = ChecklistManager("test_project")
    
    # Crear tareas
    task1 = checklist.create_task(
        title="Tarea 1",
        description="Primera tarea",
        assigned_to="architect",
        priority=TaskPriority.HIGH
    )
    print(f"   ✅ Tarea creada: {task1.id}")
    
    task2 = checklist.create_task(
        title="Tarea 2",
        description="Segunda tarea",
        assigned_to="backend_developer",
        priority=TaskPriority.MEDIUM,
        depends_on=[task1.id]
    )
    print(f"   ✅ Tarea con dependencia creada: {task2.id}")
    
    # Probar flujo
    checklist.start_task(task1.id)
    print(f"   ✅ Tarea iniciada: {task1.id}")
    
    checklist.complete_task(task1.id, {"result": "ok"})
    print(f"   ✅ Tarea completada: {task1.id}")
    
    checklist.approve_task(task1.id, "Approved!")
    print(f"   ✅ Tarea aprobada: {task1.id}")
    
    # Verificar que task2 ahora esté disponible
    next_task = checklist.get_next_task()
    assert next_task.id == task2.id, "La siguiente tarea debería ser task2"
    print(f"   ✅ Siguiente tarea correcta: {next_task.title}")
    
    # Reporte de progreso
    report = checklist.get_progress_report()
    print(f"\n   📊 Progreso: {report['progress_percentage']}%")
    print(f"   📊 Total tareas: {report['total_tasks']}")
    
    # 3. Test RollbackManager (sin CheckpointHandler para evitar problemas)
    print("\n3️⃣  Test: RollbackManager")
    from core.memory.rollback_manager import RollbackManager
    
    rollback_mgr = RollbackManager(checkpoints_dir='./data/test_checkpoints')
    
    # Crear checkpoint
    checkpoint = await rollback_mgr.checkpoint(
        project_id="test",
        state={"data": "test_state"},
        version=1,
        description="Test checkpoint"
    )
    print(f"   ✅ Checkpoint creado: {checkpoint.id}")
    
    # Listar checkpoints
    checkpoints = await rollback_mgr.list_checkpoints("test")
    print(f"   ✅ Checkpoints encontrados: {len(checkpoints)}")
    
    # Rollback
    restored = await rollback_mgr.rollback("test")
    assert restored == {"data": "test_state"}, "Estado restaurado incorrectamente"
    print(f"   ✅ Rollback exitoso")
    
    # Limpiar
    await rollback_mgr.delete_checkpoint(checkpoint.id, "test")
    print(f"   ✅ Checkpoint eliminado")
    
    # 4. Test Contratos Pydantic
    print("\n4️⃣  Test: Contratos Pydantic")
    from mcps.contracts.backend_developer_contracts import (
        BackendDeveloperInputContract,
        BackendCodeFile,
        APIEndpoint
    )
    from mcps.contracts.frontend_developer_contracts import (
        FrontendDeveloperInputContract,
        UIComponent
    )
    
    # Backend contract
    backend_input = BackendDeveloperInputContract(
        component_name="UserAPI",
        component_type="api",
        requirements=["CRUD de usuarios"]
    )
    print(f"   ✅ Backend contract válido: {backend_input.component_name}")
    
    # Frontend contract
    frontend_input = FrontendDeveloperInputContract(
        component_name="UserList",
        component_type="component",
        requirements=["Listar usuarios"]
    )
    print(f"   ✅ Frontend contract válido: {frontend_input.component_name}")
    
    # Endpoint model
    endpoint = APIEndpoint(
        method="POST",
        path="/api/users",
        description="Create user",
        response_schema={"id": "string"}
    )
    print(f"   ✅ APIEndpoint válido: {endpoint.method} {endpoint.path}")
    
    # UI Component model
    component = UIComponent(
        name="Button",
        type="functional",
        description="Reusable button"
    )
    print(f"   ✅ UIComponent válido: {component.name}")
    
    print("\n✅ TODOS LOS TESTS DE COMPONENTES PASARON")
    print("=" * 70)


async def test_mcp_contracts():
    """Test de contratos MCP sin instanciar los MCPs completos"""
    print("\n🧪 TEST: CONTRATOS MCP")
    print("=" * 70)
    
    from mcps.contracts.architect_contracts import ArchitectInputContract, ComponentSpec
    from mcps.contracts.backend_developer_contracts import ServiceDefinition  
    from mcps.contracts.frontend_developer_contracts import StyleDefinition
    from mcps.contracts.tester_contracts import TesterInputContract
    
    # Architect
    arch_input = ArchitectInputContract(feature_description="Sistema de auth")
    print(f"✅ Architect contract: {arch_input.feature_description}")
    
    comp = ComponentSpec(
        name="AuthService",
        type="backend",
        description="Servicio de autenticación",
        dependencies=[],
        estimated_complexity="medium"
    )
    print(f"✅ ComponentSpec: {comp.name}")
    
    # Backend
    service = ServiceDefinition(
        name="UserService",
        methods=["create", "read", "update", "delete"],
        dependencies=["database"],
        description="CRUD de usuarios"
    )
    print(f"✅ ServiceDefinition: {service.name}")
    
    # Frontend
    style = StyleDefinition(
        file_path="styles/app.css",
        type="css",
        classes=["container", "button"]
    )
    print(f"✅ StyleDefinition: {style.file_path}")
    
    # Tester
    tester_input = TesterInputContract(
        component_name="UserAPI",
        code_files=[{"path": "api/users.py", "content": "# code"}]
    )
    print(f"✅ Tester contract: {tester_input.component_name}")
    
    print("\n✅ TODOS LOS CONTRATOS SON VÁLIDOS")
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUITE DE TESTS SIMPLIFICADA: WORKFLOW V2")
    print("="*70 + "\n")
    
    # Test de componentes
    asyncio.run(test_workflow_components())
    
    # Test de contratos  
    asyncio.run(test_mcp_contracts())
    
    print("\n" + "="*70)
    print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE!")
    print("="*70 + "\n")
