from redis.asyncio import Redis
import json
from datetime import datetime, timedelta
import pytz
from app.config import REDIS_URL, CACHE_TZ


redis_client = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


def _now_tz() -> datetime:
    """Возвращает текущее время с учётом таймзоны."""
    tz = pytz.timezone(CACHE_TZ)
    return datetime.now(tz)

def seconds_until_next_1411() -> int:
    """Вычисляет кол-во секунд до ближайших 14:11 (TTL)."""
    now = _now_tz()
    target_today = now.replace(hour=14, minute=11, second=0, microsecond=0)
    if now >= target_today:
        target = target_today + timedelta(days=1)
    else:
        target = target_today
    return int((target - now).total_seconds())


def make_cache_key(path: str, params: dict) -> str:
    """Генерирует уникальный ключ для Redis-кэша на основе пути эндпоинта и параметров запроса."""
    payload = json.dumps(params, sort_keys=True, ensure_ascii=False)
    return f"Spimex cache:{path}:{payload}"


async def cache_get(key: str):
    """
    Получает данные из Redis по ключу.
    Return: распарсенный JSON или None, если ключ отсутствует.
    """
    raw = await redis_client.get(key)
    return json.loads(raw) if raw else None


async def cache_set(key: str, value, expire_to_1411: bool = True):
    """
    Сохраняет данные в Redis с TTL.
    По умолчанию истекает в ближайшее 14:11, иначе через 3600 секунд (1 час).
    """
    ttl = seconds_until_next_1411() if expire_to_1411 else 3600
    await redis_client.set(key, json.dumps(value, ensure_ascii=False, default=str), ex=ttl)
