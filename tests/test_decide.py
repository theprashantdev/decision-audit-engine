import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_decide_success(client):
    mock = {"decision": "APPROVE", "confidence": 0.92, "reasoning": "Looks good."}
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, return_value=mock):
        r = await client.post("/api/decide", json={"prompt": "Should we approve?"})
    assert r.status_code == 200
    d = r.json()
    assert d["decision"] == "APPROVE"
    assert d["escalated"] is False
    assert d["audit_id"].startswith("aud_")


@pytest.mark.asyncio
async def test_decide_escalation(client):
    mock = {"decision": "UNCERTAIN", "confidence": 0.4, "reasoning": "Not sure."}
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, return_value=mock):
        r = await client.post("/api/decide", json={"prompt": "Risky", "threshold": 0.75})
    assert r.status_code == 200
    assert r.json()["escalated"] is True


@pytest.mark.asyncio
async def test_decide_llm_failure(client):
    with patch("app.routes.decide.call_llm", new_callable=AsyncMock, side_effect=Exception("down")):
        r = await client.post("/api/decide", json={"prompt": "fail"})
    assert r.status_code == 502


@pytest.mark.asyncio
async def test_audit_history_empty(client):
    r = await client.get("/api/audit/history/all")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_audit_not_found(client):
    r = await client.get("/api/audit/aud_doesnotexist")
    assert r.status_code == 404


def test_escalation_logic():
    from app.engine.escalator import should_escalate, escalation_reason
    assert should_escalate(0.4, 0.75) is True
    assert should_escalate(0.9, 0.75) is False
    assert "critically" in escalation_reason(0.3, 0.75).lower()


def test_hash_chaining():
    from app.db.models import AuditDecision
    data = {"id": "x", "decision": "APPROVE", "confidence": 0.9, "prompt": "test"}
    h1 = AuditDecision.compute_hash(data, None)
    h2 = AuditDecision.compute_hash(data, h1)
    assert h1 != h2
    assert len(h1) == 64
    assert len(h2) == 64
