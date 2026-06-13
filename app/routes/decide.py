import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import AuditDecision
from app.engine.decider import call_llm
from app.engine.escalator import should_escalate
from app.core.config import settings
import json

router = APIRouter(prefix="/api", tags=["decide"])

class DecisionRequest(BaseModel):
    prompt: str
    context: dict | None = None
    threshold: float | None = None

class DecisionResponse(BaseModel):
    decision: str
    confidence: float
    reasoning: str
    escalated: bool
    escalation_reason: str | None
    audit_id: str
    timestamp: str

@router.post("/decide", response_model=DecisionResponse)
async def make_decision(req: DecisionRequest, db: AsyncSession = Depends(get_db)):
    try:
        llm_result = await call_llm(req.prompt, req.context)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {str(e)}")

    decision = llm_result.get("decision", "UNKNOWN")
    confidence = float(llm_result.get("confidence", 0.5))
    reasoning = llm_result.get("reasoning", "")
    threshold = req.threshold or settings.escalation_threshold
    escalated = should_escalate(confidence, threshold)

    # Get last hash for chain integrity
    last = await db.scalar(select(AuditDecision.entry_hash).order_by(AuditDecision.created_at.desc()).limit(1))
    audit_id = f"aud_{uuid.uuid4().hex[:20]}"
    entry_data = {"id": audit_id, "decision": decision, "confidence": confidence, "prompt": req.prompt}
    entry_hash = AuditDecision.compute_hash(entry_data, last)

    record = AuditDecision(
        id=audit_id,
        prompt=req.prompt,
        context_json=json.dumps(req.context) if req.context else None,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        escalated=escalated,
        model_used=settings.openrouter_model,
        prev_hash=last,
        entry_hash=entry_hash,
    )
    db.add(record)
    await db.commit()

    return DecisionResponse(
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        escalated=escalated,
        escalation_reason=f"Confidence {confidence:.2f} below threshold {threshold:.2f}" if escalated else None,
        audit_id=audit_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
