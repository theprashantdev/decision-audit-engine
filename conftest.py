import os
os.environ["OPENROUTER_API_KEY"] = "dummy_key_for_ci"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

@pytest_asyncio.fixture
async def async_db():
    from app.db.models import Base
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(async_db):
    from app.db.session import get_db
    from app.main import app
    async def _override():
        yield async_db
    app.dependency_overrides[get_db] = _override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
