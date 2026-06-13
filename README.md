# 🧠 Decision Audit Engine

> Every AI decision leaves a trace. Every trace is reviewable. Every review is actionable.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

## What This Solves

Every production AI system eventually faces this question: **"Why did it decide that?"**

Most systems can't answer. This engine solves that. It wraps any LLM call and automatically records:
- The full input context
- The model's output
- A confidence score
- A structured reasoning trace
- Whether human escalation was triggered
- A tamper-evident audit log entry

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────┐
│   Client    │───▶│  FastAPI Server  │───▶│  LLM Provider  │
│  (any app)  │    │  /api/decide     │    │  (OpenRouter)  │
└─────────────┘    └────────┬─────────┘    └───────┬────────┘
                            │                       │
                   ┌────────▼─────────┐             │
                   │  Audit Logger    │◀────────────┘
                   │  - confidence    │
                   │  - trace         │
                   │  - escalation    │
                   └────────┬─────────┘
                            │
                   ┌────────▼─────────┐
                   │   PostgreSQL     │
                   │  audit_decisions │
                   └──────────────────┘
```

## Quick Start

```bash
git clone https://github.com/theprashantdev/decision-audit-engine
cd decision-audit-engine
pip install -r requirements.txt
cp .env.example .env  # add your OpenRouter API key
python -m uvicorn app.main:app --reload
```

API will be live at `http://localhost:8000`

## API Reference

### `POST /api/decide`
Send a prompt, get a decision + full audit record.

```json
{
  "prompt": "Should we approve this loan application?",
  "context": { "applicant_score": 720, "loan_amount": 50000 },
  "threshold": 0.8
}
```

**Response:**
```json
{
  "decision": "APPROVE",
  "confidence": 0.91,
  "reasoning": "Score above threshold, amount within acceptable range...",
  "escalated": false,
  "audit_id": "aud_01HX...",
  "timestamp": "2026-06-13T16:30:00Z"
}
```

### `GET /api/audit/{audit_id}`
Retrieve any past decision by its audit ID.

### `GET /api/audit/history?limit=50`
Full paginated audit history with filtering.

### `GET /api/audit/escalations`
All decisions that triggered human escalation.

## Key Features

- ✅ **Zero-config audit logging** — every call automatically recorded
- ✅ **Confidence scoring** — model uncertainty quantified per decision
- ✅ **Auto-escalation** — low-confidence decisions flagged for human review
- ✅ **Tamper-evident logs** — SHA-256 chained audit entries
- ✅ **Full REST API** — drop into any existing system
- ✅ **Async PostgreSQL** — production-ready persistence

## Project Structure

```
decision-audit-engine/
├── app/
│   ├── main.py           # FastAPI entrypoint
│   ├── routes/
│   │   ├── decide.py     # Decision endpoint
│   │   └── audit.py      # Audit retrieval endpoints
│   ├── engine/
│   │   ├── decider.py    # Core LLM decision logic
│   │   ├── scorer.py     # Confidence scoring
│   │   └── escalator.py  # Escalation logic
│   ├── db/
│   │   ├── models.py     # SQLAlchemy models
│   │   └── session.py    # DB connection
│   └── core/
│       └── config.py     # Settings & env
├── tests/
│   ├── test_decide.py
│   └── test_audit.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT © [Prashant Raj](https://github.com/theprashantdev)
