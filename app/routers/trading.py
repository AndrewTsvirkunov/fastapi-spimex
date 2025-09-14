from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated
from app.db import get_async_db
from app.crud import get_last_trading_dates, get_dynamics, get_trading_results
from app.schemas import TradingResultsResponse, TradingDatesResponse, DynamicsRequest, TradingResultsRequest
from cache import cache_get, cache_set, make_cache_key


router = APIRouter(prefix="/trading", tags=["trading"])


@router.get("/last-dates", response_model=TradingDatesResponse)
async def last_trading_dates(
        days: Annotated[int, Query(gt=0, le=365, description="Количество последних дат")] = 1,
        db: AsyncSession = Depends(get_async_db)):
    """
    Получает список дат последних торгов.

    Обязательный параметр days (сколько последних торговых дней)
    Обоснование: без него неоднозначно, сколько дат возвращать. Значение по умолчанию - 1 (последний день).

    Return: Dict[str, List[TradingDatesResponse]]: список дат.
    """
    params = {"dates": days}
    key = make_cache_key("/last-dates", params)
    cached = await cache_get(key)
    if cached:
        return cached

    dates = await get_last_trading_dates(days, db)
    result = {"dates": dates}

    await cache_set(key, result)
    return result


@router.get("/dynamics", response_model=List[TradingResultsResponse])
async def dynamics(request: DynamicsRequest = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Получает результаты торгов за указанный период.
    Return: List[TradingResultsResponse]: Список Pydantic объектов с результатами торгов.
    """
    if request.start_date > request.end_date:
        raise HTTPException(status_code=400, detail="start_date должен быть раньше end_date")

    params = {
        "start_date": str(request.start_date),
        "end_date": str(request.end_date),
        "oil_id": request.oil_id,
        "delivery_type_id": request.delivery_type_id,
        "delivery_basis_id": request.delivery_basis_id,
        "limit": request.limit,
    }
    key = make_cache_key("/dynamics", params)
    cached = await cache_get(key)
    if cached:
        return cached

    orm_result = await get_dynamics(request, db)
    result = [TradingResultsResponse.model_validate(r).model_dump() for r in orm_result]

    await cache_set(key, result)
    return result


@router.get("/results", response_model=List[TradingResultsResponse])
async def trading_results(request: TradingResultsRequest = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Получает результаты торгов за после дни (days).
    Return: List[TradingResultsResponse]: Список Pydantic объектов с результатами торгов.
    """
    params = {
        "days": request.days,
        "oil_id": request.oil_id,
        "delivery_type_id": request.delivery_type_id,
        "delivery_basis_id": request.delivery_basis_id,
        "limit": request.limit,
    }
    key = make_cache_key("/results", params)
    cached = await cache_get(key)
    if cached:
        return cached

    orm_result = await get_trading_results(request, db)
    result = [TradingResultsResponse.model_validate(r).model_dump() for r in orm_result]

    await cache_set(key, result)
    return result