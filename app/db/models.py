import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class AuditDecision(Base):
    __tablename__ = "audit_decisions"

    id = Column(String, primary_key=True)
    prompt = Column(Text, nullable=False)
    context_json = Column(Text, nullable=True)
    decision = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(Text, nullable=False)
    escalated = Column(Boolean, default=False)
    model_used = Column(String(255), nullable=False)
    prev_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    @classmethod
    def compute_hash(cls, data: dict, prev_hash: str | None) -> str:
        payload = json.dumps(data, sort_keys=True, default=str) + (prev_hash or "")
        return hashlib.sha256(payload.encode()).hexdigest()
