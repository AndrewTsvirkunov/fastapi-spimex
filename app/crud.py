from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import Optional

from app.models import SpimexTradingResult


async def get_last_trading_dates(db: AsyncSession, days: int):
    """
    Получает список дат последних торгов.
    Return: List[datetime]: список дат.
    """
    q = (
        select(SpimexTradingResult.date)
        .group_by(SpimexTradingResult.date)
        .order_by(SpimexTradingResult.date.desc())
        .limit(days)
    )
    result = await db.execute(q)
    return [r[0] for r in result.all()]


async def get_dynamics(db: AsyncSession, start_date: date, end_date: date,
                       oil_id: Optional[str] = None, delivery_type_id: Optional[str] = None,
                       delivery_basis_id: Optional[str] = None, limit: int = 1000):
    """
    Получает результаты торгов за указанный период.
    Return: List[SpimexTradingResult]: Список ORM-объектов с результатами торгов.
    """
    q = (
        select(SpimexTradingResult)
        .where(SpimexTradingResult.date >= start_date,
               SpimexTradingResult.date <= end_date)
        .order_by(SpimexTradingResult.date.asc())
        .limit(limit)
    )
    if oil_id:
        q = q.where(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        q = q.where(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        q = q.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

    result = await db.execute(q)
    return result.scalars().all()


async def get_trading_results(db: AsyncSession,
                              days: int,
                              oil_id: Optional[str] = None,
                              delivery_type_id: Optional[str] = None,
                              delivery_basis_id: Optional[str] = None,
                              limit: int = 1000):
    """
    Получает результаты торгов за после дни (days).
    Return: List[SpimexTradingResult]: Список ORM-объектов с результатами торгов.
    """
    dates_q = (
        select(SpimexTradingResult.date)
        .group_by(SpimexTradingResult.date)
        .order_by(SpimexTradingResult.date.desc())
        .limit(days)
    )
    last_dates = await db.execute(dates_q)
    last_dates_res = [r[0] for r in last_dates.all()]
    if not last_dates_res:
        return []
    q = select(SpimexTradingResult).where(SpimexTradingResult.date.in_(last_dates_res))
    if oil_id:
        q = q.where(SpimexTradingResult.oil_id == oil_id)
    if delivery_type_id:
        q = q.where(SpimexTradingResult.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        q = q.where(SpimexTradingResult.delivery_basis_id == delivery_basis_id)
    q = q.order_by(SpimexTradingResult.date.desc()).limit(limit)

    result = await db.execute(q)
    return result.scalars().all()