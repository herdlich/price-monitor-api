from fastapi import FastAPI, HTTPException, status
from pathlib import Path
import logging

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

app = FastAPI()

db_init(DB_PATH)

Path("data").mkdir(exist_ok=True)


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_product(payload: AddProduct):
    permitted_domain = "https://store.steampowered.com/"
    if payload.link[:31] != permitted_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Disallowed URL: This domain is not permitted"
        )

    added_product = add_product_by_link(payload.link)
    if not added_product:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return added_product


@app.get("/products", response_model=list[ProductResponse])
def get_products():
    all_products = get_all_products(DB_PATH)
    if not all_products:
        logger.warning("No products have been added")

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return all_products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = get_product_by_id(DB_PATH, product_id)
    if not product:
        logger.warning("Product with ID %s not found", product_id)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return product


@app.get("/products/{product_id}/price-history", response_model=list[PriceHistoryResponse])
def get_price_history(product_id: int):
    product_history = get_the_price_history_by_id(DB_PATH, product_id)
    if not product_history:
        logger.warning("No product history found for %s ID", product_id)

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return product_history


@app.delete("/products/{product_id}", response_model=ProductResponse)
def delete_product(product_id: int):
    product = get_product_by_id(DB_PATH, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    delete_product_by_id(DB_PATH, product_id)

    return product


@app.post("/products/refresh-prices", response_model=list[UpdatedPriceHistoryResponse])
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
