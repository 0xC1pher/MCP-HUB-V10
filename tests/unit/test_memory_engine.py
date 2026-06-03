"""
Tests para ConsistentMemoryEngine
"""
import pytest
import asyncio
import tempfile
from pathlib import Path

from core.memory.event_store import PersistentEventStore
from core.memory.memory_engine import ConsistentMemoryEngine


@pytest.fixture
async def memory_engine():
    """Fixture para Memory Engine con EventStore temporal"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_events.db"
        event_store = PersistentEventStore(db_path=str(db_path))
        await event_store.initialize()
        
        engine = ConsistentMemoryEngine(event_store)
        yield engine


@pytest.mark.asyncio
async def test_memory_write_basic(memory_engine):
    """Test: Escritura básica en memoria"""
    result = await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="architect",
        event_type="plan_created",
        data={"plan": "test_plan"}
    )
    
    assert result['status'] == 'success'
    assert result['version'] == 1
    assert 'event_id' in result


@pytest.mark.asyncio
async def test_memory_read_basic(memory_engine):
    """Test: Lectura básica de memoria"""
    # Escribir datos
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="architect",
        event_type="plan_created",
        data={"plan": "test_plan"}
    )
    
    # Leer datos
    state = await memory_engine.read_memory("test_project")
    
    assert state['project_id'] == "test_project"
    assert state['version'] == 1
    assert 'plan' in state['data']


@pytest.mark.asyncio
async def test_memory_cache(memory_engine):
    """Test: Cache de memoria funciona correctamente"""
    # Primera lectura (carga desde DB)
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="test",
        event_type="test",
        data={"key": "value"}
    )
    
    state1 = await memory_engine.read_memory("test_project", use_cache=True)
    
    # Segunda lectura (debe venir de cache)
    state2 = await memory_engine.read_memory("test_project", use_cache=True)
    
    assert state1 == state2


@pytest.mark.asyncio
async def test_conflict_detection_last_write_wins(memory_engine):
    """Test: Detección y resolución de conflictos con Last-Write-Wins"""
    # Escribir versión 1
    result1 = await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="mcp1",
        event_type="test",
        data={"value": 1}
    )
    
    # Escribir versión 2 con versión esperada correcta
    result2 = await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="mcp2",
        event_type="test",
        data={"value": 2},
        expected_version=1
    )
    
    assert result2['status'] == 'success'
    assert result2['version'] == 2


@pytest.mark.asyncio
async def test_conflict_resolution_triggers(memory_engine):
    """Test: Resolución de conflictos se activa correctamente"""
    # Escribir versión 1
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="mcp1",
        event_type="test",
        data={"value": 1}
    )
    
    # Escribir con versión esperada incorrecta (conflicto)
    result = await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="mcp2",
        event_type="test",
        data={"value": 2},
        expected_version=0  # Versión incorrecta
    )
    
    # Debe detectar y resolver el conflicto
    assert result['status'] == 'success'
    assert result['conflict_resolved'] == True


@pytest.mark.asyncio
async def test_incremental_cache_update(memory_engine):
    """Test: Cache se actualiza incrementalmente"""
    # Primera escritura
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="architect",
        event_type="plan_created",
        data={"plan": "plan1"}
    )
    
    # Leer para popular cache
    state1 = await memory_engine.read_memory("test_project")
    
    # Segunda escritura
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="developer",
        event_type="code_generated",
        data={"file": "test.py"}
    )
    
    # Leer nuevamente
    state2 = await memory_engine.read_memory("test_project")
    
    assert state2['version'] == 2
    assert state2['events_count'] == 2


@pytest.mark.asyncio
async def test_cache_invalidation(memory_engine):
    """Test: Invalidación de cache"""
    # Escribir y leer
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="test",
        event_type="test",
        data={}
    )
    
    await memory_engine.read_memory("test_project")
    
    # Invalidar cache
    await memory_engine.invalidate_cache("test_project")
    
    # Verificar que funciona después de invalidación
    state = await memory_engine.read_memory("test_project")
    assert state is not None


@pytest.mark.asyncio
async def test_memory_stats(memory_engine):
    """Test: Estadísticas del memory engine"""
    # Escribir algunos datos
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="test",
        event_type="test",
        data={}
    )
    
    # Obtener stats
    stats = await memory_engine.get_memory_stats()
    
    assert 'cache_size' in stats
    assert 'pending_writes' in stats
    assert 'total_events' in stats
    assert stats['total_events'] >= 1


@pytest.mark.asyncio
async def test_multiple_projects(memory_engine):
    """Test: Manejo de múltiples proyectos"""
    # Escribir en proyecto 1
    await memory_engine.write_memory(
        project_id="project1",
        mcp_source="test",
        event_type="test",
        data={"project": 1}
    )
    
    # Escribir en proyecto 2
    await memory_engine.write_memory(
        project_id="project2",
        mcp_source="test",
        event_type="test",
        data={"project": 2}
    )
    
    # Leer ambos
    state1 = await memory_engine.read_memory("project1")
    state2 = await memory_engine.read_memory("project2")
    
    assert state1['project_id'] == "project1"
    assert state2['project_id'] == "project2"


@pytest.mark.asyncio
async def test_version_specific_read(memory_engine):
    """Test: Lectura de versión específica"""
    # Escribir múltiples versiones
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="test",
        event_type="test",
        data={"version": 1}
    )
    
    await memory_engine.write_memory(
        project_id="test_project",
        mcp_source="test",
        event_type="test",
        data={"version": 2}
    )
    
    # Leer versión específica
    state_v1 = await memory_engine.read_memory("test_project", version=1)
    
    assert state_v1['version'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
