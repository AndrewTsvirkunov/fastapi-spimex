import pytest
from datetime import date

from app.crud import get_last_trading_dates, get_dynamics, get_trading_results
from app.schemas import DynamicsRequest, TradingResultsRequest


@pytest.mark.asyncio
async def test_get_last_trading_dates(session, sample_trading_results):
    """
    Проверяет функцию get_last_trading_dates:
    1. Возвращает правильное количество последних дат торгов.
    2. Содержит дату, соответствующую последней записи.
    """
    result = await get_last_trading_dates(1, session)
    assert len(result) == 1
    assert sample_trading_results[1].date in result


@pytest.mark.asyncio
async def test_get_dynamics(session, sample_trading_results):
    """
    Проверяет функцию get_dynamics:
    Возвращает результаты торгов за заданный период, учитывая limit.
    """
    request = DynamicsRequest(
        start_date=date(2025, 9, 12),
        end_date=date(2025, 9, 13),
        oil_id=None,
        delivery_type_id=None,
        delivery_basis_id=None,
        limit=10
    )
    result = await get_dynamics(request, session)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_trading_results(session, sample_trading_results):
    """
    Проверяет функцию get_trading_results:
    Возвращает результаты за последние 2 дня, учитывая limit.
    """
    request = TradingResultsRequest(
        days=2,
        oil_id=None,
        delivery_type_id=None,
        delivery_basis_id=None,
        limit=5
    )
    result = await get_trading_results(request, session)
    assert len(result) == 2
