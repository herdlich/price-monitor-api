from price_monitor_api.database import db_init, save_db


def save_products_to_db(db_file, data):
    for product in data:
        save_db(db_file, product)


def test_post_refresh_price_history(client, payload, tmp_path, monkeypatch):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    fake_history_changes = {
        "id": 2,
        "name": "Tainted Grail: The Fall of Avalon",
        "new_price": 19.99,
        "old_price": 21.99,
        "actual_currency": "€",
        "discount": "Discount",
    }

    monkeypatch.setattr(
        "price_monitor_api.api.check_actual_products",
        lambda db: [fake_history_changes]
    )

    response_refresh_prices = client.post("/products/refresh-prices")

    expected_response = [
        {
            "id": 2,
            "name": "Tainted Grail: The Fall of Avalon",
            "new_price": 19.99,
            "old_price": 21.99,
            "actual_currency": "€",
            "discount": "Discount",
        }
    ]

    assert response_refresh_prices.status_code == 200
    assert response_refresh_prices.json() == expected_response
