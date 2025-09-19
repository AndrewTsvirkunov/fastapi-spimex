import pytest
from datetime import date


@pytest.mark.asyncio
async def test_dynamics_with_mock_cache(client, mocker):
    """
    Проверяет, что эндпоинт /trading/dynamics возвращает данные напрямую из кеша,
    если cache_get отдает результат.
    """
    fake_data = [{
        "exchange_product_id": "A106ROR005A",
        "exchange_product_name": "Бензин (АИ-100-К5) EURO-6",
        "oil_id": "A106",
        "delivery_basis_id": "ROR",
        "delivery_basis_name": "НБ Серпуховская",
        "delivery_type_id": "005A",
        "volume": 100,
        "total": 200,
        "count": 3,
        "date": "2025-09-12"
    }]

    mocker.patch("app.routers.trading.cache_get", return_value=fake_data)

    params = {
        "start_date": date(2025, 9, 12),
        "end_date": date(2025, 9, 13)
    }
    response = await client.get("trading/dynamics", params=params)

    assert response.status_code == 200
    assert response.json() == fake_data