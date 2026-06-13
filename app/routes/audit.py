from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.session import get_db
from app.db.models import AuditDecision
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/audit", tags=["audit"])

class AuditRecord(BaseModel):
    id: str
    prompt: str
    decision: str
    confidence: float
    reasoning: str
    escalated: bool
    model_used: str
    entry_hash: str
    created_at: str

@router.get("/{audit_id}", response_model=AuditRecord)
async def get_audit(audit_id: str, db: AsyncSession = Depends(get_db)):
    record = await db.get(AuditDecision, audit_id)
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return AuditRecord(
        id=record.id, prompt=record.prompt, decision=record.decision,
        confidence=record.confidence, reasoning=record.reasoning,
        escalated=record.escalated, model_used=record.model_used,
        entry_hash=record.entry_hash, created_at=str(record.created_at)
    )

@router.get("/history/all", response_model=List[AuditRecord])
async def get_history(limit: int = Query(50, le=200), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditDecision).order_by(desc(AuditDecision.created_at)).limit(limit))
    records = result.scalars().all()
    return [AuditRecord(id=r.id, prompt=r.prompt, decision=r.decision, confidence=r.confidence,
                        reasoning=r.reasoning, escalated=r.escalated, model_used=r.model_used,
                        entry_hash=r.entry_hash, created_at=str(r.created_at)) for r in records]

@router.get("/escalations/all", response_model=List[AuditRecord])
async def get_escalations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditDecision).where(AuditDecision.escalated == True).order_by(desc(AuditDecision.created_at)))
    records = result.scalars().all()
    return [AuditRecord(id=r.id, prompt=r.prompt, decision=r.decision, confidence=r.confidence,
                        reasoning=r.reasoning, escalated=r.escalated, model_used=r.model_used,
                        entry_hash=r.entry_hash, created_at=str(r.created_at)) for r in records]
