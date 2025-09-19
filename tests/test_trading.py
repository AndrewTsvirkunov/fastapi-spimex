import pytest
from datetime import date


@pytest.mark.asyncio
async def test_last_trading_dates_endpoint(client, sample_trading_results):
    """
    Проверяет, что эндпоинт /trading/last-dates возвращает 2 последние даты торгов.
    """
    params = {"days": 2}
    response = await client.get("/trading/last-dates", params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data["dates"]) == 2


@pytest.mark.asyncio
async def test_dynamics_endpoint(client, sample_trading_results):
    """
    Проверяет, что эндпоинт /trading/dynamics возвращает результаты торгов за указанный период.
    """
    params = {
        "start_date": date(2025, 9, 12),
        "end_date": date(2025, 9, 13),
        "limit": 50
    }
    response = await client.get("/trading/dynamics", params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_trading_results_endpoint(client, sample_trading_results):
    """
    Проверяет, что эндпоинт /trading/results возвращает только последний 1 день торгов.
    """
    params = {
        "days": 1,
        "limit": 20
    }
    response = await client.get("/trading/results", params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
