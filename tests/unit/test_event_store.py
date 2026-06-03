"""
Tests para PersistentEventStore
"""
import pytest
import asyncio
import os
import tempfile
from pathlib import Path

from core.memory.event_store import PersistentEventStore, Event


@pytest.fixture
async def event_store():
    """Fixture para EventStore con DB temporal"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_events.db"
        store = PersistentEventStore(db_path=str(db_path))
        await store.initialize()
        yield store


@pytest.mark.asyncio
async def test_event_store_initialization(event_store):
    """Test: Inicialización correcta del Event Store"""
    # Verificar que se pueden agregar eventos
    event = await event_store.append_event(
        project_id="test_project",
        mcp_source="architect",
        event_type="test_event",
        data={"test": "data"}
    )
    
    assert event.id is not None
    assert event.project_id == "test_project"
    assert event.mcp_source == "architect"
    assert event.event_type == "test_event"


@pytest.mark.asyncio
async def test_event_append_and_retrieve(event_store):
    """Test: Agregar y recuperar eventos"""
    # Agregar eventos
    event1 = await event_store.append_event(
        project_id="project1",
        mcp_source="architect",
        event_type="plan_created",
        data={"plan": "test_plan"}
    )
    
    event2 = await event_store.append_event(
        project_id="project1",
        mcp_source="developer",
        event_type="code_generated",
        data={"code": "test_code"}
    )
    
    # Recuperar eventos
    events = await event_store.get_events(project_id="project1")
    
    assert len(events) == 2
    assert events[0].id == event1.id
    assert events[1].id == event2.id


@pytest.mark.asyncio
async def test_event_versioning(event_store):
    """Test: Versionado automático de eventos"""
    # Agregar múltiples eventos
    await event_store.append_event(
        project_id="project1",
        mcp_source="architect",
        event_type="test",
        data={}
    )
    
    await event_store.append_event(
        project_id="project1",
        mcp_source="developer",
        event_type="test",
        data={}
    )
    
    # Verificar versiones incrementales
    latest_version = await event_store.get_latest_version("project1")
    assert latest_version == 2


@pytest.mark.asyncio
async def test_event_filtering(event_store):
    """Test: Filtrado de eventos por criterios"""
    # Agregar eventos de diferentes tipos
    await event_store.append_event(
        project_id="project1",
        mcp_source="architect",
        event_type="plan_created",
        data={}
    )
    
    await event_store.append_event(
        project_id="project1",
        mcp_source="developer",
        event_type="code_generated",
        data={}
    )
    
    # Filtrar por event_type
    plan_events = await event_store.get_events(
        project_id="project1",
        event_type="plan_created"
    )
    
    assert len(plan_events) == 1
    assert plan_events[0].event_type == "plan_created"


@pytest.mark.asyncio
async def test_project_state_reconstruction(event_store):
    """Test: Reconstrucción de estado desde eventos"""
    # Agregar secuencia de eventos
    await event_store.append_event(
        project_id="project1",
        mcp_source="architect",
        event_type="plan_created",
        data={"plan": "feature_plan"}
    )
    
    await event_store.append_event(
        project_id="project1",
        mcp_source="developer",
        event_type="code_generated",
        data={"file": "models.py", "content": "code"}
    )
    
    # Reconstruir estado
    state = await event_store.get_project_state("project1")
    
    assert state['project_id'] == "project1"
    assert state['version'] == 2
    assert 'plan' in state['data']
    assert 'code_files' in state['data']


@pytest.mark.asyncio
async def test_version_range_query(event_store):
    """Test: Consulta de eventos por rango de versiones"""
    # Agregar múltiples eventos
    for i in range(5):
        await event_store.append_event(
            project_id="project1",
            mcp_source="test",
            event_type="test",
            data={"index": i}
        )
    
    # Consultar rango específico
    events = await event_store.get_events(
        project_id="project1",
        from_version=2,
        to_version=4
    )
    
    assert len(events) == 3
    assert events[0].version == 2
    assert events[-1].version == 4


@pytest.mark.asyncio
async def test_count_events(event_store):
    """Test: Contar eventos"""
    # Agregar eventos
    for i in range(3):
        await event_store.append_event(
            project_id="project1",
            mcp_source="test",
            event_type="test",
            data={}
        )
    
    # Contar
    count = await event_store.count_events(project_id="project1")
    assert count == 3
    
    total_count = await event_store.count_events()
    assert total_count >= 3


@pytest.mark.asyncio
async def test_multiple_projects_isolation(event_store):
    """Test: Aislamiento entre proyectos"""
    # Agregar eventos a diferentes proyectos
    await event_store.append_event(
        project_id="project1",
        mcp_source="test",
        event_type="test",
        data={}
    )
    
    await event_store.append_event(
        project_id="project2",
        mcp_source="test",
        event_type="test",
        data={}
    )
    
    # Verificar aislamiento
    project1_events = await event_store.get_events(project_id="project1")
    project2_events = await event_store.get_events(project_id="project2")
    
    assert len(project1_events) == 1
    assert len(project2_events) == 1
    assert project1_events[0].project_id == "project1"
    assert project2_events[0].project_id == "project2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
