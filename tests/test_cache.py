import pytest
import json
import pytz
from datetime import datetime

from cache import _now_tz, seconds_until_next_1411, make_cache_key, cache_get, cache_set, redis_client
from app.config import CACHE_TZ


def test_now_tz():
    """
    Проверяет datetime.now с таймзоной Europe/Moscow.
    """
    datetime_now = _now_tz()
    assert datetime_now == datetime.now(pytz.timezone(CACHE_TZ))


def test_seconds_until_next_1411():
    """
    Проверяет TTl, который лежит в диапазоне от 0 до 24 часов
    """
    seconds = seconds_until_next_1411()
    assert 0 < seconds < 24 * 60 * 60


def test_make_cache_key():
    """
    Проверяет, что функция make_cache_key:
    1. Генерирует одинаковый ключ при разном порядке параметров.
    2. Добавляет префикс "Spimex cache:<path>:".
    """
    path = "/test-trading/dynamics"
    params = {"oil_id": "A692", "delivery_type_id": "F"}
    key1 = make_cache_key(path, params)
    key2 = make_cache_key(path, {"delivery_type_id": "F", "oil_id": "A692"})
    assert key1 == key2
    assert key1.startswith("Spimex cache:/test-trading/dynamics:")


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """
    Проверяет корректность записи и чтения из Redis:
    1. cache_set сохраняет данные в Redis.
    2. cache_get возвращает их в исходном виде.
    3. Данные в хранилище совпадают с JSON-значением.
    """
    key = make_cache_key("/test-trading/results", {"delivery_basis_id": "BIN"})
    value = {"delivery_basis_id": "SUR"}

    await cache_set(key, value, expire_to_1411=False)
    cached = await cache_get(key)

    assert cached == value

    raw = await redis_client.get(key)
    assert json.loads(raw) == value
