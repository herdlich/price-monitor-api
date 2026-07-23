from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AddProduct(BaseModel):
    link: str


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    currency: str
    discount: str
    link: str
    created_at: str


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    currency: str
    discount: str
    checked_at: str


class UpdatedPriceHistoryResponse(BaseModel):
    id: int
    name: str
    new_price: float
    old_price: float
    actual_currency: str
    discount: str
