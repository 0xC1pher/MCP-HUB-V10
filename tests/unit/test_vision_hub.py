"""
Tests for VisionHub
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from core.vision.vision_hub import VisionHub, VisionCache, AnalyzeRequest

@pytest.fixture
def mock_model_router():
    router = MagicMock()
    router.generate = AsyncMock(return_value="Fallback text description.")
    return router

@pytest.fixture
def vision_hub(mock_model_router, tmp_path):
    # Use a temporary unique JSON file for each test cache
    cache_file = tmp_path / "test_vision_cache.json"
    hub = VisionHub(llm_provider=mock_model_router)
    hub.cache = VisionCache(disk_path=str(cache_file))
    return hub

@pytest.fixture
def client(vision_hub):
    return TestClient(vision_hub.app)

def test_analyze_cache_hit(client):
    request = AnalyzeRequest(
        image_base64="data:image/jpeg;base64,/9j/testimage",
        prompt="Test prompt"
    )
    
    # First call - cache miss
    response1 = client.post("/analyze", json=request.model_dump())
    assert response1.status_code == 200
    data1 = response1.json()
    assert not data1["from_cache"]
    
    # Second call - cache hit
    response2 = client.post("/analyze", json=request.model_dump())
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["from_cache"]

def test_analyze_fallback(vision_hub, client, monkeypatch):
    # Mock vision failure
    monkeypatch.setattr(vision_hub, '_process_vision', AsyncMock(side_effect=Exception("Vision error")))
    
    request = AnalyzeRequest(image_base64="data:image/jpeg;base64/error", prompt="Error prompt")
    response = client.post("/analyze", json=request.model_dump())
    data = response.json()
    assert data["fallback_used"]
    assert "Fallback text description" in data["caption"]

def test_metrics(client):
    response = client.get("/metrics")
    metrics = response.json()
    assert isinstance(metrics, dict)
    assert 'vision_analyses' in metrics
