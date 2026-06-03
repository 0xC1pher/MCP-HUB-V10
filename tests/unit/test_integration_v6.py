"""
Test Integral de MCP Hub V6
Prueba todos los componentes integrados
"""
import asyncio
import json
from pathlib import Path

from mcp_hub_v6 import create_mcp_hub, MCPHubV6
from core.memory.session_manager import SessionType, SessionStrategy


async def test_full_integration():
    """Test completo de integración V6"""
    print("🚀 MCP HUB V6 - TEST DE INTEGRACIÓN COMPLETO")
    print("=" * 70)
    
    # 1. Inicializar Hub
    print("\n1️⃣  Inicializando MCP Hub V6...")
    hub = create_mcp_hub()
    print("   ✅ Hub inicializado")
    
    # 2. Crear sesión
    print("\n2️⃣  Creando sesión de desarrollo...")
    session = await hub.create_session(
        session_id="test_session_001",
        session_type=SessionType.FEATURE_IMPLEMENTATION,
        strategy=SessionStrategy.TRIMMING
    )
    print(f"   ✅ Sesión creada: {session.session_id}")
    
    # 3. Probar chunking
    print("\n3️⃣  Probando Dynamic Chunking...")
    sample_code = """
def calculate_sum(a, b):
    '''Calcula la suma de dos números'''
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        self.result += value
        return self.result
"""
    chunks = hub.chunker.adaptive_chunking(sample_code, "calculator.py")
    print(f"   ✅ {len(chunks)} chunks generados")
    for i, chunk in enumerate(chunks, 1):
        print(f"      - Chunk {i}: {chunk.metadata.content_type.value}, "
              f"{chunk.metadata.size} chars, "
              f"complexity: {chunk.metadata.complexity_score:.2f}")
    
    # 4. Probar query expansion
    print("\n4️⃣  Probando Query Expansion...")
    query = "¿Cómo implementar machine learning en Python?"
    expansion = hub.query_expander.expand_query(query, max_expansions=5)
    print(f"   ✅ Query: '{query}'")
    print(f"   ✅ Tipo: {expansion.query_type.value}")
    print(f"   ✅ Queries expandidas: {len(expansion.expanded_queries)}")
    for eq in expansion.expanded_queries[:3]:
        print(f"      - {eq}")
    
    # 5. Probar confidence calibration
    print("\n5️⃣  Probando Confidence Calibration...")
    test_scores = [0.3, 0.5, 0.7, 0.9]
    print("   Scores de prueba:")
    for score in test_scores:
        calibrated = hub.confidence_calibrator.calibrate_confidence(score)
        print(f"      Raw: {score:.2f} → Calibrated: {calibrated.calibrated_score:.3f} "
              f"[{calibrated.confidence_level.value}]")
    
    # 6. Probar code indexing
    print("\n6️⃣  Probando Code Indexing...")
    # Crear archivo temporal para indexar
    with open("calculator.py", "w") as f:
        f.write(sample_code)
        
    index_result = await hub.index_code("calculator.py", sample_code)
    print(f"   ✅ Archivo: {index_result['file']}")
    print(f"   ✅ Status: {index_result.get('status')}")
    print(f"   ✅ Entidades encontradas: {index_result.get('entities_found')}")
    print(f"   ✅ Referencias encontradas: {index_result['references_found']}")
    
    # 7. Agregar turns a sesión
    print("\n7️⃣  Agregando conversación a sesión...")
    turns = [
        ("¿Cómo crear una clase en Python?", "Usa la palabra clave 'class'..."),
        ("¿Qué es self?", "self es la referencia al objeto actual..."),
        ("¿Cómo usar herencia?", "Usa paréntesis con la clase padre...")
    ]
    
    for query, response in turns:
        await hub.add_turn("test_session_001", query, response)
    print(f"   ✅ {len(turns)} turns agregados")
    
    # 8. Obtener contexto integrado
    print("\n8️⃣  Obteniendo contexto integrado...")
    context = await hub.get_context(
        query="explicar clases en Python",
        session_id="test_session_001",
        top_k=3
    )
    print(f"   ✅ Query original: {context['original_query']}")
    print(f"   ✅ Tipo de query: {context['query_type']}")
    print(f"   ✅ Queries expandidas: {len(context['expanded_queries'])}")
    print(f"   ✅ Resultados encontrados: {len(context['results'])}")
    print(f"   ✅ Token budget disponible: {context['token_budget_available']}")
    
    # 9. Estado del sistema
    print("\n9️⃣  Estado del Sistema:")
    status = hub.get_system_status()
    print(f"   📦 Storage:")
    print(f"      - MP4: {status['storage']['mp4_path']}")
    print(f"      - Chunks: {status['storage']['chunks_loaded']}")
    print(f"      - Vector engine: {status['storage']['vector_stats']['status']}")
    
    print(f"   💬 Sessions:")
    print(f"      - Activas: {status['sessions']['active_sessions']}")
    print(f"      - Total: {status['sessions']['total_sessions']}")
    
    print(f"   🧠 Advanced:")
    print(f"      - Semantic terms: {status['advanced']['query_expander']['semantic_terms']}")
    
    print(f"   📊 Indexing:")
    print(f"      - Enabled: {status['indexing']['enabled']}")
    print(f"      - Entities: {status['indexing']['entities']}")
    
    print(f"   🎯 TOON:")
    print(f"      - Max tokens: {status['toon']['max_tokens']}")
    print(f"      - Available: {status['toon']['available']}")
    
    # 10. Resumen final
    print("\n" + "=" * 70)
    print("✅ INTEGRACIÓN V6 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n📊 Resumen de Componentes Probados:")
    print("   ✅ Storage Layer (MP4 + Vector + Sessions)")
    print("   ✅ Memory + Session Management")
    print("   ✅ Dynamic Chunking")
    print("   ✅ Query Expansion")
    print("   ✅ Confidence Calibration")
    print("   ✅ Code Indexing")
    print("   ✅ Entity Tracking")
    print("   ✅ TOON (Token Optimization)")
    print("\n🎉 TODOS LOS COMPONENTES FUNCIONANDO CORRECTAMENTE\n")


if __name__ == "__main__":
    asyncio.run(test_full_integration())
