"""
Test Multi-Agent Workflow
Prueba el flujo completo Orquestador -> Architect -> Developer -> Tester
"""
import asyncio
from mcp_hub_v6 import create_mcp_hub
from core.orchestrator import Orchestrator

async def test_workflow():
    print("🤖 MULTI-AGENT WORKFLOW TEST")
    print("=" * 60)
    
    # 1. Init Hub & Orchestrator
    print("\n1️⃣  Inicializando Sistema...")
    hub = create_mcp_hub()
    orchestrator = Orchestrator(hub)
    await orchestrator.start()
    print("   ✅ Orquestador y Agentes iniciados")
    
    # 2. Execute Workflow
    feature = "Sistema de autenticación de usuarios con login y registro"
    print(f"\n2️⃣  Ejecutando Workflow para: '{feature}'")
    
    result = await orchestrator.execute_feature_request(feature)
    
    # 3. Analyze Results
    print("\n3️⃣  Resultados del Workflow:")
    
    if "error" in result and "plan" not in result:
        print(f"   ❌ Error crítico: {result.get('error')}")
        return

    # Plan info
    plan = result.get("plan", {})
    print(f"   📋 Plan Generado (ID: {plan.get('plan_id')})")
    print(f"      Riesgos: {', '.join(plan.get('risks', []))}")
    
    # Components info
    components = result.get("components", [])
    print(f"\n   🏭 Componentes Implementados ({len(components)}):")
    
    for comp in components:
        name = comp['name']
        status = comp['status']
        impl = comp['implementation']
        val = comp['validation']
        
        status_icon = "✅" if status == "completed" else "⚠️"
        print(f"\n      {status_icon} Component: {name}")
        
        # Code stats
        files = impl.get('code_files', [])
        print(f"         Archivos: {len(files)}")
        for f in files:
            print(f"           - {f['path']} ({len(f['content'])} chars)")
            
        # Validation stats
        passed = val.get('validation_passed', False)
        issues = val.get('issues', [])
        print(f"         Validación: {'PASSED' if passed else 'FAILED'}")
        if issues:
            print(f"         Problemas ({len(issues)}):")
            for issue in issues:
                print(f"           - [{issue['severity']}] {issue['message']}")

    await orchestrator.stop()
    print("\n✅ TEST FINALIZADO")

if __name__ == "__main__":
    asyncio.run(test_workflow())
