import pytest
import pytest_asyncio
import asyncio
import sys
from datetime import date, datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db import get_async_db
from app.models import Base, SpimexTradingResult
from app.main import app
from cache import redis_client
from app.config import TEST_DATABASE_URL


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, poolclass=NullPool)
async_session_test = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Фикстура создает и чистит тестовую БД один раз на сессию.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """
    Фикстура создает сессию для тестовой БД.
    """
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    """
    Асинхронный HTTP клиент для тестирования FastAPI.
    Подменяет зависимость get_async_db на тестовую сессию.
    После завершения теста сбрасывает переопределения зависимостей.
    """
    async def override_get_db():
        async with session.begin():
            yield session

    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_trading_results(session):
    """
    Фикстура для наполнения тестовой таблицы spimex_trading_results данными.
    1. Очищает таблицу перед вставкой новых данных.
    2. Возвращает список ORM-объектов для использования в тестах.
    """
    await session.execute(text("TRUNCATE spimex_trading_results RESTART IDENTITY CASCADE;"))
    data = [
        SpimexTradingResult(
            exchange_product_id="A106ROR005A",
            exchange_product_name="Бензин (АИ-100-К5) EURO-6, НБ Серпуховская (самовывоз автотранспортом)",
            oil_id="A106",
            delivery_basis_id="ROR",
            delivery_basis_name="НБ Серпуховская",
            delivery_type_id="A",
            volume=50,
            total=5350000,
            count=2,
            date=date(2025, 9, 12),
            created_on=datetime.now(),
            updated_on=datetime.now()
        ),
        SpimexTradingResult(
            exchange_product_id="A10KZLY060W",
            exchange_product_name="Бензин (АИ-100-К5)-Евро, ст. Злынка-Экспорт (промежуточная станция)",
            oil_id="A10K",
            delivery_basis_id="ZLY",
            delivery_basis_name="ст. Злынка-Экспорт",
            delivery_type_id="W",
            volume=60,
            total=5760000,
            count=1,
            date=date(2025, 9, 13),
            created_on=datetime.now(),
            updated_on=datetime.now()
        )
    ]
    session.add_all(data)
    await session.commit()
    return data


@pytest.fixture(autouse=True)
@pytest.mark.asyncio
async def redis_cleanup():
    """
    Фикстура автоматически закрывает Redis после каждого теста.
    """
    yield
    if redis_client:
        await redis_client.close()
        await redis_client.connection_pool.disconnect()
