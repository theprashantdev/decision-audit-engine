from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import init_db
from app.routes import decide, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Decision Audit Engine",
    description="Production-grade AI decision logging with confidence scoring and escalation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(decide.router)
app.include_router(audit.router)

@app.get("/")
async def root():
    return {"service": "Decision Audit Engine", "version": "1.0.0", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "ok"}
