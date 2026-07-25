from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    field_validator
)


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AddProduct(BaseModel):
    link: HttpUrl

    @field_validator("link")
    @classmethod
    def validate_steam_links(cls, url: HttpUrl) -> HttpUrl:
        if url.scheme != "https":
            raise ValueError("Only HTTPS links are permitted")
        if url.host != "store.steampowered.com":
            raise ValueError("Only store.steampowered.com links permitted")

        return url


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
