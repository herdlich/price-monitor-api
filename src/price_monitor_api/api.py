from fastapi import FastAPI, HTTPException, status
from pathlib import Path
import logging

from .exceptions import ProductAlreadyExistsError

from .database import (
    db_init,
    get_all_products,
    get_product_by_id,
    get_the_price_history_by_id,
    delete_product_by_id,
)

from .main import add_product_by_link, check_actual_products
from .config import DB_PATH
from .models import AddProduct, ProductResponse, PriceHistoryResponse, UpdatedPriceHistoryResponse

logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "Products",
        "description": "Product and Price History Management",
    }
]

app = FastAPI(
    title="Price Monitor API",
    description="API for a price monitor project",
    version="1.0.0",
    openapi_tags=tags_metadata

)

db_init(DB_PATH)

Path("data").mkdir(exist_ok=True)


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"]
)
def add_product(payload: AddProduct):
    try:
        added_product = add_product_by_link(str(payload.link), DB_PATH)
    except ProductAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "product_already_exists",
                "message": str(exc),
                "product_name": exc.product_name
            }
        ) from exc

    if not added_product:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return added_product


@app.get(
    "/products",
    response_model=list[ProductResponse],
    tags=["Products"]
)
def get_products():
    all_products = get_all_products(DB_PATH)
    if not all_products:
        logger.warning("No products have been added")

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return all_products


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"]
)
def get_product(product_id: int):
    product = get_product_by_id(DB_PATH, product_id)
    if not product:
        logger.warning("Product with ID %s not found", product_id)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return product


@app.get(
    "/products/{product_id}/price-history",
    response_model=list[PriceHistoryResponse],
    tags=["Products"]
)
def get_price_history(product_id: int):
    product_history = get_the_price_history_by_id(DB_PATH, product_id)
    if not product_history:
        logger.warning("No product history found for %s ID", product_id)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return product_history


@app.delete(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Products"]
)
def delete_product(product_id: int):
    product = get_product_by_id(DB_PATH, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    delete_product_by_id(DB_PATH, product_id)

    return product


@app.post(
    "/products/refresh-prices",
    response_model=list[UpdatedPriceHistoryResponse],
    tags=["Products"]
)
def refresh_product_prices():
    products = check_actual_products(DB_PATH)
    if products is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="database is empty"
        )

    if not products:
        return []

    return products
