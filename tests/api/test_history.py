from price_monitor_api.database import db_init, save_db


def save_products_to_db(db_file, data):
    for product in data:
        save_db(db_file, product)


def test_get_product_history_by_id(client, payload, tmp_path):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    response_get = client.get("/products/2/price-history")

    expected_response = [
        {
            "id": 2,
            "product_id": 2,
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
        }
    ]

    response_get_data = response_get.json()

    assert response_get.status_code == 200

    [product.pop("checked_at") for product in response_get_data]

    assert response_get_data == expected_response
