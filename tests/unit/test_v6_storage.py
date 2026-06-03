"""
Tests for V6 Storage Layer
"""
import pytest
import asyncio
import tempfile
from pathlib import Path
import numpy as np

from core.storage.mp4_storage import MP4Storage, VirtualChunk
from core.storage.vector_engine import VectorEngine
from core.storage.session_storage import SessionStorage


@pytest.fixture
def temp_dir():
    """Temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def vector_config():
    """Vector engine configuration"""
    return {
        'embedding': {
            'model': 'sentence-transformers/all-MiniLM-L6-v2',
            'dimension': 384,
            'normalize': True,
            'dtype': 'float16'
        },
        'hnsw': {
            'ef_construction': 200,
            'M': 16,
            'ef_search': 50
        }
    }


# MP4Storage Tests

def test_mp4_storage_initialization(temp_dir):
    """Test: MP4Storage initializes correctly"""
    mp4_path = Path(temp_dir) / "test.mp4"
    storage = MP4Storage(str(mp4_path))
    
    assert storage.mp4_path == mp4_path
    assert len(storage.chunks) == 0
    assert storage.metadata == {}


def test_virtual_chunk_creation():
    """Test: VirtualChunk created from dict"""
    chunk_data = {
        'chunk_id': 'test_123',
        'file_path': '/tmp/test.md',
        'start_line': 0,
        'end_line': 10,
        'vector_offset': 0,
        'vector_size': 384,
        'section': 'Introduction',
        'summary': 'Test summary',
        'text_hash': 'abc123'
    }
    
    chunk = VirtualChunk.from_dict(chunk_data)
    
    assert chunk.chunk_id == 'test_123'
    assert chunk.section == 'Introduction'
    assert chunk.to_dict() == chunk_data


def test_mp4_storage_empty_initialization(temp_dir):
    """Test: MP4Storage can create empty storage"""
    mp4_path = Path(temp_dir) / "empty.mp4"
    storage = MP4Storage(str(mp4_path))
    
    storage.initialize_empty_storage()
    
    assert mp4_path.exists()
    assert storage.load_snapshot()
    assert len(storage.chunks) == 0


# VectorEngine Tests

def test_vector_engine_initialization(vector_config):
    """Test: VectorEngine initializes with config"""
    engine = VectorEngine(vector_config)
    
    assert engine.dimension == 384
    assert engine.model_name == 'sentence-transformers/all-MiniLM-L6-v2'
    assert engine.ef_construction == 200
    assert engine.M == 16


def test_vector_engine_create_index(vector_config):
    """Test: VectorEngine can create HNSW index"""
    engine = VectorEngine(vector_config)
    engine.create_index(100)
    
    assert engine.index is not None
    stats = engine.get_stats()
    assert stats['status'] == 'ready'
    assert stats['dimension'] == 384


def test_vector_engine_add_and_search(vector_config):
    """Test: VectorEngine can add vectors and search"""
    engine = VectorEngine(vector_config)
    engine.create_index(10)
    
    # Create dummy vectors
    vectors = np.random.rand(5, 384).astype(np.float32)
    chunk_ids = [f'chunk_{i}' for i in range(5)]
    
    # Add vectors
    engine.add_vectors(vectors, chunk_ids)
    
    assert len(engine.id_to_chunk_id) == 5
    assert len(engine.chunk_id_to_id) == 5
    
    # Search
    query = np.random.rand(384).astype(np.float32)
    results, scores = engine.search(query, top_k=3)
    
    assert len(results) == 3
    assert len(scores) == 3
    assert all(isinstance(r, str) for r in results)
    assert all(isinstance(s, float) for s in scores)


# SessionStorage Tests

@pytest.mark.asyncio
async def test_session_storage_initialization(temp_dir):
    """Test: SessionStorage initializes correctly"""
    storage = SessionStorage(storage_dir=temp_dir, retention_days=30)
    
    assert storage.storage_dir == Path(temp_dir)
    assert storage.retention_days == 30


@pytest.mark.asyncio
async def test_session_storage_save_and_load_turn(temp_dir):
    """Test: SessionStorage can save and load turns"""
    storage = SessionStorage(storage_dir=temp_dir)
    
    # Save turn
    turn_data = {
        'query': 'What is Python?',
        'response': 'Python is a programming language',
        'metadata': {'test': True}
    }
    
    await storage.save_turn('test_session', turn_data)
    
    # Load session
    turns = await storage.load_session('test_session')
    
    assert len(turns) == 1
    assert turns[0]['query'] == 'What is Python?'
    assert 'timestamp' in turns[0]


@pytest.mark.asyncio
async def test_session_storage_metadata(temp_dir):
    """Test: SessionStorage manages metadata"""
    storage = SessionStorage(storage_dir=temp_dir)
    
    # Save metadata
    metadata = {
        'session_id': 'test_session',
        'session_type': 'feature',
        'strategy': 'trimming'
    }
    
    await storage.save_metadata('test_session', metadata)
    
    # Load metadata
    loaded = await storage.load_metadata('test_session')
    
    assert loaded['session_id'] == 'test_session'
    assert loaded['session_type'] == 'feature'


@pytest.mark.asyncio
async def test_session_storage_list_sessions(temp_dir):
    """Test: SessionStorage can list sessions"""
    storage = SessionStorage(storage_dir=temp_dir)
    
    # Create multiple sessions
    for i in range(3):
        await storage.save_turn(f'session_{i}', {'query': f'test_{i}'})
    
    # List sessions
    sessions = await storage.list_sessions()
    
    assert len(sessions) == 3
    assert 'session_0' in sessions
    assert 'session_1' in sessions
    assert 'session_2' in sessions


@pytest.mark.asyncio
async def test_session_storage_delete(temp_dir):
    """Test: SessionStorage can delete sessions"""
    storage = SessionStorage(storage_dir=temp_dir)
    
    # Create session
    await storage.save_turn('test_delete', {'query': 'test'})
    
    # Verify exists
    sessions = await storage.list_sessions()
    assert 'test_delete' in sessions
    
    # Delete
    deleted = await storage.delete_session('test_delete')
    assert deleted is True
    
    # Verify deleted
    sessions = await storage.list_sessions()
    assert 'test_delete' not in sessions


@pytest.mark.asyncio
async def test_session_storage_summary(temp_dir):
    """Test: SessionStorage generates summaries"""
    storage = SessionStorage(storage_dir=temp_dir)
    
    # Setup session with metadata and turns
    metadata = {
        'session_id': 'summary_test',
        'session_type': 'bugfix',
        'strategy': 'summarizing'
    }
    await storage.save_metadata('summary_test', metadata)
    
    # Add turns
    for i in range(3):
        await storage.save_turn('summary_test', {'query': f'query_{i}'})
    
    # Get summary
    summary = await storage.get_session_summary('summary_test')
    
    assert summary is not None
    assert summary['session_id'] == 'summary_test'
    assert summary['turn_count'] == 3
    assert summary['session_type'] == 'bugfix'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
