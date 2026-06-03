"""
Tests for VisionHub
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from core.vision.vision_hub import VisionHub, AnalyzeRequest

@pytest.fixture
def mock_model_router():
    router = MagicMock()
    router.generate = AsyncMock(return_value="Fallback text description.")
    return router

@pytest_asyncio.fixture
async def vision_hub(mock_model_router):
    hub = VisionHub(llm_provider=mock_model_router)
    return hub

@pytest.mark.asyncio
async def test_analyze_cache_hit(vision_hub):
    request = AnalyzeRequest(
        image_base64="data:image/jpeg;base64,/9j/testimage",
        prompt="Test prompt"
    )
    
    # First call - cache miss
    response1 = await vision_hub.app.post("/analyze", json=request.dict())
    assert response1.status_code == 200
    data1 = response1.json()
    assert not data1["from_cache"]
    
    # Second call - cache hit
    response2 = await vision_hub.app.post("/analyze", json=request.dict())
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["from_cache"]

@pytest.mark.asyncio
async def test_analyze_fallback(vision_hub, monkeypatch):
    # Mock vision failure
    monkeypatch.setattr(vision_hub, '_process_vision', AsyncMock(side_effect=Exception("Vision error")))
    
    request = AnalyzeRequest(image_base64="data:image/jpeg;base64/error", prompt="Error prompt")
    response = await vision_hub.app.post("/analyze", json=request.dict())
    data = response.json()
    assert data["fallback_used"]
    assert "Fallback text description" in data["caption"]

@pytest.mark.asyncio
async def test_metrics(vision_hub):
    response = await vision_hub.app.get("/metrics")
    metrics = response.json()
    assert isinstance(metrics, dict)
    assert 'vision_analyses' in metrics
