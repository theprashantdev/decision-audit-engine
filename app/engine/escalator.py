from app.core.config import settings

def should_escalate(confidence: float, threshold: float | None = None) -> bool:
    limit = threshold if threshold is not None else settings.escalation_threshold
    return confidence < limit

def escalation_reason(confidence: float, threshold: float) -> str:
    gap = threshold - confidence
    if gap > 0.3:
        return f"Confidence critically low ({confidence:.2f}). Human review required."
    elif gap > 0.15:
        return f"Confidence below threshold ({confidence:.2f} < {threshold:.2f}). Flagged for review."
    else:
        return f"Confidence marginally below threshold ({confidence:.2f}). Soft escalation."
