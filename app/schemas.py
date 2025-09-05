from pydantic import BaseModel, Field
from datetime import date as date_type


class TradingResultOut(BaseModel):
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


class TradingDatesOut(BaseModel):
    """
    Схема ответа для эндпоинта, возвращающего список дат последних торговых дней.
    """
    dates: list[date_type] = Field(..., description="Список торговых дат")
