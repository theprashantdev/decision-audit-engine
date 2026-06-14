import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_decide_endpoint_success():
    mock_llm = {"decision": "APPROVE", "confidence": 0.92, "reasoning": "Test reasoning."}
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, return_value=mock_llm):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/decide", json={"prompt": "Should we approve this?"})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "APPROVE"
    assert data["confidence"] == 0.92
    assert data["audit_id"].startswith("aud_")
    assert data["escalated"] is False


@pytest.mark.asyncio
async def test_decide_endpoint_escalation():
    mock_llm = {"decision": "UNCERTAIN", "confidence": 0.4, "reasoning": "Low confidence."}
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, return_value=mock_llm):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/decide", json={"prompt": "Risky decision", "threshold": 0.75})
    assert response.status_code == 200
    data = response.json()
    assert data["escalated"] is True
    assert data["escalation_reason"] is not None


@pytest.mark.asyncio
async def test_decide_llm_failure_returns_502():
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, side_effect=Exception("upstream down")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/decide", json={"prompt": "fail test"})
    assert response.status_code == 502


@pytest.mark.asyncio
async def test_audit_history_empty():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/audit/history/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_escalation_logic():
    from app.engine.escalator import should_escalate, escalation_reason
    assert should_escalate(0.4, 0.75) is True
    assert should_escalate(0.9, 0.75) is False
    reason = escalation_reason(0.3, 0.75)
    assert "critically low" in reason
