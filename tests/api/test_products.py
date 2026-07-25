from price_monitor_api.database import db_init, save_db
from pathlib import Path
from datetime import datetime


def save_products_to_db(db_file, data):
    for product in data:
        save_db(db_file, product)


def test_post_product(client, tmp_path, monkeypatch):
    path_db = tmp_path / "data" / "products.db"
    current_dir = Path(__file__).parent
    path_html = current_dir.parent / "fixtures" / "steam" / "regular_product.html"

    db_init(path_db)

    with open(path_html, "r", encoding="utf-8") as file:
        fake_html_text = file.read()

    monkeypatch.setattr(
        "price_monitor_api.main.get_html",
        lambda url: fake_html_text
    )

    response_post = client.post(
        "/products",
        json={"link": "https://store.steampowered.com/app/3949040/RV_There_Yet/"}
    )

    expected_response_post_without_created_at = {
        "id": 1,
        "name": "RV There Yet?",
        "price": 7.79,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/",
        "app_id": 3949040,
    }

    # test for POST
    assert response_post.status_code == 201

    response_post_data = response_post.json()
    created_at = response_post_data.pop("created_at")

    assert response_post_data == expected_response_post_without_created_at

    assert datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

    # GET test after POST
    response_get = client.get("/products")

    expected_response_get = [
        {
            "id": 1,
            "name": "RV There Yet?",
            "price": 7.79,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/",
            "app_id": 3949040,
        }
    ]

    response_get_data = response_get.json()

    assert response_get.status_code == 200

    [product.pop("created_at", None) for product in response_get_data]

    assert response_get_data == expected_response_get


def test_get_all_products(client, payload, tmp_path):
    path_db = tmp_path / "data" / "products.db"
    db_init(path_db)

    save_products_to_db(path_db, payload)

    expected_response = [
        {
            "id": 1,
            "name": "MECCHA CHAMELEON",
            "price": 6.15,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
            "app_id": 4704690,
            "created_at": "2026-07-22 19:14:15",
        },
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "app_id": 1466060,
            "created_at": "2026-07-23 12:28:08",
        }
    ]

    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_response == response.json()


def test_get_product_by_id(client, payload, tmp_path):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    expected_response = {
        "id": 2,
        "name": "Tainted Grail: The Fall of Avalon",
        "price": 21.99,
        "currency": "€",
        "discount": "Discount",
        "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
        "app_id": 1466060,
        "created_at": "2026-07-23 12:28:08",
    }

    response = client.get("/products/2")

    assert response.status_code == 200
    assert response.json() == expected_response


def test_delete_product_by_id(client, payload, tmp_path):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    expected_deleted_response = {
        "id": 1,
        "name": "MECCHA CHAMELEON",
        "price": 6.15,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
        "app_id": 4704690,
        "created_at": "2026-07-22 19:14:15",
    }

    response_delete = client.delete("/products/1")

    assert response_delete.status_code == 200
    assert response_delete.json() == expected_deleted_response

    response = client.get("/products")

    expected_response = [
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "app_id": 1466060,
            "created_at": "2026-07-23 12:28:08",
        }
    ]

    assert response.status_code == 200
    assert response.json() == expected_response
