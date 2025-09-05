from sqlalchemy import Integer, Float, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, datetime
from app.db import Base


class SpimexTradingResult(Base):
    """
    ORM-модель таблицы spimex_trading_results.
    """
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    exchange_product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    oil_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    delivery_basis_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    delivery_basis_name: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_type_id: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_on: Mapped[datetime] = mapped_column(DateTime, nullable=False)