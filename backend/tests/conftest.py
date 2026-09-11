import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database.models import Base
from app.database.repositories import ResearchRepository
from app.database.connection import get_db
from app.llm.mock import MockLLMProvider
from app.search.mock import MockSearch
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_session():
    """Create a fresh in-memory SQLite database for test isolation."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_repo(test_db_session):
    return ResearchRepository(test_db_session)


@pytest.fixture
def mock_llm():
    return MockLLMProvider(embedding_dim=1536)


@pytest.fixture
def mock_search():
    return MockSearch()


@pytest_asyncio.fixture
async def async_client(test_db_session):
    """FastAPI AsyncClient overriding database dependency."""
    async def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
