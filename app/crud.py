from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import SpimexTradingResult
from app.schemas import DynamicsRequest, TradingResultsRequest


async def get_last_trading_dates(days: int, db: AsyncSession):
    """
    Получает список дат последних торгов.
    Return: List[datetime]: список дат.
    """
    q = (
        select(SpimexTradingResult.date.distinct())
        .order_by(SpimexTradingResult.date.desc())
        .limit(days)
    )
    result = await db.execute(q)
    return [r[0] for r in result.all()]


async def get_dynamics(request: DynamicsRequest, db: AsyncSession):
    """
    Получает результаты торгов за указанный период.
    Return: List[SpimexTradingResult]: Список ORM-объектов с результатами торгов.
    """
    q = (
        select(SpimexTradingResult)
        .where(SpimexTradingResult.date >= request.start_date,
               SpimexTradingResult.date <= request.end_date)
        .order_by(SpimexTradingResult.date.asc())
        .limit(request.limit)
    )
    if request.oil_id:
        q = q.where(SpimexTradingResult.oil_id == request.oil_id)
    if request.delivery_type_id:
        q = q.where(SpimexTradingResult.delivery_type_id == request.delivery_type_id)
    if request.delivery_basis_id:
        q = q.where(SpimexTradingResult.delivery_basis_id == request.delivery_basis_id)

    result = await db.execute(q)
    return result.scalars().all()


async def get_trading_results(request: TradingResultsRequest, db: AsyncSession):
    """
    Получает результаты торгов за после дни (days).
    Return: List[SpimexTradingResult]: Список ORM-объектов с результатами торгов.
    """
    dates_q = (
        select(SpimexTradingResult.date.distinct())
        .order_by(SpimexTradingResult.date.desc())
        .limit(request.days)
    )
    last_dates = await db.execute(dates_q)
    last_dates_res = [r[0] for r in last_dates.all()]

    if not last_dates_res:
        return []

    min_date = min(last_dates_res)
    max_date = max(last_dates_res)

    q = select(SpimexTradingResult).where(
        SpimexTradingResult.date >= min_date,
        SpimexTradingResult.date <= max_date
    )

    if request.oil_id:
        q = q.where(SpimexTradingResult.oil_id == request.oil_id)
    if request.delivery_type_id:
        q = q.where(SpimexTradingResult.delivery_type_id == request.delivery_type_id)
    if request.delivery_basis_id:
        q = q.where(SpimexTradingResult.delivery_basis_id == request.delivery_basis_id)

    q = q.order_by(SpimexTradingResult.date.desc()).limit(request.limit)

    result = await db.execute(q)
    return result.scalars().all()