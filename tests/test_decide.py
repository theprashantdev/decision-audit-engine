import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_decide_endpoint_structure():
    mock_llm = {"decision": "APPROVE", "confidence": 0.92, "reasoning": "Test reasoning."}
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, return_value=mock_llm):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/decide", json={"prompt": "Test decision"})
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert "confidence" in data
    assert "audit_id" in data
    assert data["audit_id"].startswith("aud_")
