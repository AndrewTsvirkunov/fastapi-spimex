from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional, List, Annotated
from app.db import get_async_db
from app.crud import get_last_trading_dates, get_dynamics, get_trading_results
from app.schemas import TradingResultOut, TradingDatesOut
from cache import cache_get, cache_set, make_cache_key


router = APIRouter(prefix="/trading", tags=["trading"])


@router.get("/last-dates", response_model=TradingDatesOut)
async def last_trading_dates(
        days: Annotated[int, Query(gt=0, le=365, description="Количество последних дат")] = 1,
        db: AsyncSession = Depends(get_async_db)):
    """
    Получает список дат последних торгов.

    Обязательный параметр days (сколько последних торговых дней)
    Обоснование: без него неоднозначно, сколько дат возвращать. Значение по умолчанию - 1 (последний день).

    Return: List[dict[str, TradingDatesOut]]: список дат.
    """
    params = {"dates": days}
    key = make_cache_key("/last-dates", params)
    cached = await cache_get(key)
    if cached:
        return cached

    dates = await get_last_trading_dates(db, days)
    result = {"dates": dates}

    await cache_set(key, result)
    return result


@router.get("/dynamics", response_model=List[TradingResultOut])
async def dynamics(
    start_date: Annotated[date, Query(description="Начало периода (YYYY-MM-DD)")],
    end_date: Annotated[date, Query(description="Конец периода (YYYY-MM-DD)")],
    oil_id: Annotated[Optional[str], Query()] = None,
    delivery_type_id: Annotated[Optional[str], Query()] = None,
    delivery_basis_id: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query( gt=0, le=1000, description="Ограничение на число записей")] = 1000,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Получает результаты торгов за указанный период.

    Обязательные параметры: start_date и end_date.
    Обоснование: без дат определить границы периода невозможно.
    Фильтры по oil_id, delivery_type_id, delivery_basis_id - опциональны.

    Return: List[TradingResultOut]: Список Pydantic объектов с результатами торгов.
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date должен быть раньше end_date")

    params = {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "oil_id": oil_id,
        "delivery_type_id": delivery_type_id,
        "delivery_basis_id": delivery_basis_id,
        "limit": limit,
    }
    key = make_cache_key("/dynamics", params)
    cached = await cache_get(key)
    if cached:
        return cached

    orm_result = await get_dynamics(db, start_date, end_date, oil_id, delivery_type_id, delivery_basis_id, limit)
    result = [TradingResultOut.model_validate(r).model_dump() for r in orm_result]

    await cache_set(key, result)
    return result


@router.get("/results", response_model=List[TradingResultOut])
async def trading_results(
    days: Annotated[int, Query(gt=0, le=30, description="Количество последних дней")] = 1,
    oil_id: Annotated[Optional[str], Query()] = None,
    delivery_type_id: Annotated[Optional[str], Query()] = None,
    delivery_basis_id: Annotated[Optional[str], Query()] = None,
    limit: Annotated[int, Query( gt=0, le=1000, description="Ограничение на число записей")] = 1000,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Получает результаты торгов за после дни (days).

    Обязательный параметр: days (по умолчанию 1) - сколько последних торговых дат включить.
    Обоснование: термин в условии задачи 'последние торги' без уточнения размера неоднозначен.
    Фильтры по oil_id, delivery_type_id, delivery_basis_id - опциональны.

    Return: List[TradingResultOut]: Список Pydantic объектов с результатами торгов.
    """
    params = {
        "days": days,
        "oil_id": oil_id,
        "delivery_type_id": delivery_type_id,
        "delivery_basis_id": delivery_basis_id,
        "limit": limit,
    }
    key = make_cache_key("results", params)
    cached = await cache_get(key)
    if cached:
        return cached

    orm_result = await get_trading_results(db, days, oil_id, delivery_type_id, delivery_basis_id, limit)
    result = [TradingResultOut.model_validate(r).model_dump() for r in orm_result]

    await cache_set(key, result)
    return result