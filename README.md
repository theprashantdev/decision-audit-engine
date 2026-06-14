# Decision Audit Engine


API Endpoint:
https://decision-audit-engine-1.onrender.com

API Documentation:
https://decision-audit-engine-1.onrender.com/docs

Production-grade AI decision logging system...

> Production-grade AI decision logging system. Every LLM call produces a traceable audit record with reasoning chain, confidence score, hash-chained integrity, and automated escalation for low-confidence decisions.

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)]()
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![CI](https://github.com/theprashantdev/decision-audit-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/theprashantdev/decision-audit-engine/actions/workflows/ci.yml)

## What It Does

Every call to `/api/decide` does four things in sequence:
1. Sends the prompt and context to an LLM via OpenRouter
2. Extracts a structured decision: label, confidence score, reasoning trace
3. Writes an audit record to the database with a SHA-256 hash chained to the previous entry
4. Escalates automatically if confidence falls below the configured threshold

The result is an immutable, tamper-evident log of every AI decision your system makes — queryable, auditable, and explainable to anyone who wasn't in the room.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/decide` | Submit a prompt, get a decision + audit record |
| `GET` | `/api/audit/{id}` | Retrieve a specific audit record by ID |
| `GET` | `/api/audit/history/all` | List all decisions (paginated, default 50) |
| `GET` | `/api/audit/escalations/all` | List only escalated decisions |
| `GET` | `/health` | Health check |

## Quick Start

```bash
git clone https://github.com/theprashantdev/decision-audit-engine
cd decision-audit-engine
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set OPENROUTER_API_KEY and DATABASE_URL
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** for the interactive API docs.

## Environment Variables

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/audit_engine
ESCALATION_THRESHOLD=0.75
APP_ENV=development
SECRET_KEY=change_this_in_production
```

For local development without PostgreSQL, use SQLite:
```env
DATABASE_URL=sqlite+aiosqlite:///./audit.db
```

## Running Tests

Tests use SQLite in-memory — no database setup required.

```bash
pytest --tb=short -v
```

## Docker

```bash
docker build -t decision-audit-engine .
docker run -p 8000:8000 --env-file .env decision-audit-engine
```

## Example Request

```bash
curl -X POST http://localhost:8000/api/decide \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Should we approve this loan application?", "context": {"credit_score": 720, "income": 85000}}'
```

```json
{
  "decision": "APPROVE",
  "confidence": 0.89,
  "reasoning": "Credit score above threshold and income sufficient for requested amount.",
  "escalated": false,
  "escalation_reason": null,
  "audit_id": "aud_3f9a1c2b7d4e",
  "timestamp": "2026-06-14T06:00:00.000000+00:00"
}
```

## Architecture

```
POST /api/decide
       │
       ▼
  Input Validation (Pydantic)
       │
       ▼
  OpenRouter LLM Call
  (decision + confidence + reasoning)
       │
       ▼
  Escalation Check
  (confidence < threshold?)
       │
       ▼
  Hash Chain
  SHA-256(entry_data + prev_hash)
       │
       ▼
  Write to Database
  (AuditDecision record)
       │
       ▼
  Return Response
```

## Project Structure

```
decision-audit-engine/
├── app/
│   ├── core/
│   │   └── config.py          # Pydantic settings
│   ├── db/
│   │   ├── models.py           # SQLAlchemy models + hash logic
│   │   └── session.py          # Async engine + session factory
│   ├── engine/
│   │   ├── decider.py          # OpenRouter LLM call
│   │   └── escalator.py        # Confidence threshold logic
│   ├── routes/
│   │   ├── decide.py           # POST /api/decide
│   │   └── audit.py            # GET /api/audit/*
│   └── main.py                 # FastAPI app + lifespan
├── tests/
│   └── test_decide.py
├── conftest.py                  # SQLite test fixtures
├── pytest.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```

## License

MIT © [Prashant Raj](https://github.com/theprashantdev)
