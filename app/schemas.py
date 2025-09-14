from pydantic import BaseModel, Field
from datetime import date as date_type
from typing import Optional


class TradingResultsResponse(BaseModel):
    """
    Схема ответа для эндпоинтов, возвращающих список торгов за заданный период
    и список последних торгов.
    """
    exchange_product_id: str = Field(..., description="Код инструмента")
    exchange_product_name: str = Field(..., description="Наименование инструмента")
    oil_id: str = Field(..., description="Тип продукта")
    delivery_basis_id: str = Field(..., description="Код базиса поставки")
    delivery_basis_name: str = Field(..., description="Базис поставки")
    delivery_type_id: str = Field(..., description="Код типа поставки")
    volume: float = Field(..., description="Объем договоров в единицах измерения")
    total: float = Field(..., description="Объем договоров, руб.")
    count: int = Field(..., description="Количество договоров, шт.")
    date: date_type = Field(..., description="Торговая ата")

    model_config = {"from_attributes": True}


class TradingDatesResponse(BaseModel):
    """
    Схема ответа для эндпоинта, возвращающего список дат последних торговых дней.
    """
    dates: list[date_type] = Field(..., description="Список торговых дат")


class DynamicsRequest(BaseModel):
    """
    Схема запроса для получения динамики торговых результатов
    за указанный период с возможностью фильтрации по параметрам.

    Обязательные параметры: start_date и end_date.
    Обоснование: без дат определить границы периода невозможно.
    Фильтры по oil_id, delivery_type_id, delivery_basis_id - опциональны.
    """
    start_date: date_type = Field(date_type(2025, 9, 3), description="Начало периода (YYYY-MM-DD)")
    end_date: date_type = Field(date_type(2025, 9, 4), description="Конец периода (YYYY-MM-DD)")
    oil_id: Optional[str] = Field(None)
    delivery_type_id: Optional[str] = Field(None)
    delivery_basis_id: Optional[str] = Field(None)
    limit: int = Field(1000, gt=0, le=1000, description="Ограничение на число записей")


class TradingResultsRequest(BaseModel):
    """
    Схема запроса ля получения последних торговых результатов
    за последние дни (days) с фильтрацией по параметрам.

    Обязательный параметр: days (по умолчанию 1) - сколько последних торговых дат включить.
    Обоснование: термин в условии задачи <<последние торги>> без уточнения размера неоднозначен.
    Фильтры по oil_id, delivery_type_id, delivery_basis_id - опциональны.
    """
    days: int = Field(1, gt=0, le=30, description="Количество последних дней")
    oil_id: Optional[str] = Field(None)
    delivery_type_id: Optional[str] = Field(None)
    delivery_basis_id: Optional[str] = Field(None)
    limit: int = Field(1000, gt=0, le=1000, description="Ограничение на число записей")