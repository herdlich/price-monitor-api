import sqlite3
from price_monitor_api.database import (
    db_init,
    save_db,
    get_all_products,
    get_product_by_id,
    get_the_price_history_by_id,
    delete_product_by_id,
)


def save_products_to_db(db_file, data):
    for product in data:
        save_db(db_file, product)


def test_db_init_creates_products_table(tmp_path):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    with sqlite3.connect(path_db) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'products'
        """)

        table = cursor.fetchone()

    assert table is not None
    assert table[0] == "products"


def test_save_to_db_product_data(tmp_path):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    payload = {
        "name": "MECCHA CHAMELEON",
        "price": 6.15,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
        "created_at": "2026-07-22 19:14:15",
    }

    saved_product = save_db(path_db, payload)

    assert saved_product is not None

    expected_product = {
        "id": 1,
        "name": "MECCHA CHAMELEON",
        "price": 6.15,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
        "created_at": "2026-07-22 19:14:15",
    }

    assert saved_product == expected_product


def test_get_all_products_from_db(tmp_path, payload):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    products = get_all_products(path_db)

    assert products is not None

    expected_products = [
        {
            "id": 1,
            "name": "MECCHA CHAMELEON",
            "price": 6.15,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
            "created_at": "2026-07-22 19:14:15",
        },
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "created_at": "2026-07-23 12:28:08",
        },
    ]

    assert products == expected_products


def test_get_product_by_id(tmp_path, payload):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    product = get_product_by_id(path_db, 2)

    assert product is not None

    expected_product = {
        "id": 2,
        "name": "Tainted Grail: The Fall of Avalon",
        "price": 21.99,
        "currency": "€",
        "discount": "Discount",
        "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
        "created_at": "2026-07-23 12:28:08",
    }

    assert product == expected_product


def test_get_the_price_history_by_id(tmp_path, payload):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    product_history = get_the_price_history_by_id(path_db, 2)

    assert product_history is not None

    expected_product_history = [
        {
            "id": 2,
            "product_id": 2,
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
        }
    ]

    [product.pop("checked_at") for product in product_history]

    assert product_history == expected_product_history


def test_delete_product_by_id(tmp_path, payload):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    # Testing added products
    all_products = get_all_products(path_db)
    assert all_products is not None
    expected_products = [
        {
            "id": 1,
            "name": "MECCHA CHAMELEON",
            "price": 6.15,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
            "created_at": "2026-07-22 19:14:15",
        },
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "created_at": "2026-07-23 12:28:08",
        },
    ]
    assert all_products == expected_products

    # Deleting a product
    delete_product_by_id(path_db, 1)

    # Test the updated database
    updated_products = get_all_products(path_db)

    assert updated_products is not None

    expected_updated_products = [
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "created_at": "2026-07-23 12:28:08",
        },
    ]

    assert updated_products == expected_updated_products
