from price_monitor_api.main import (
    check_actual_products,
    product_existence_check,
    add_product_by_link,
)

from price_monitor_api.database import (
    db_init,
    save_db,
    get_all_products,
)


def save_products_to_db(db_file, data):
    for product in data:
        save_db(db_file, product)


def test_check_actual_products(tmp_path, payload, monkeypatch):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    html_responses = ["html_1", "html_2"]
    monkeypatch.setattr(
        "price_monitor_api.main.get_html",
        lambda url: html_responses.pop(0)
    )

    parser_responses = [
        {
            "name": "MECCHA CHAMELEON",
            "price": 5.22,
            "currency": "€",
            "discount": "Discount",
        },
        {
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 43.99,
            "currency": "€",
            "discount": "No discount",
        },
    ]

    def mock_parse_page(html_text):
        return parser_responses.pop(0)

    monkeypatch.setattr(
        "price_monitor_api.main.parse_page",
        mock_parse_page
    )

    actual_products = check_actual_products(path_db)

    assert actual_products is not None
    assert len(actual_products) == 2

    assert actual_products[0]["new_price"] == 5.22
    assert actual_products[0]["old_price"] == 6.15
    assert actual_products[0]["discount"] == "Discount"

    assert actual_products[1]["new_price"] == 43.99
    assert actual_products[1]["old_price"] == 21.99
    assert actual_products[1]["discount"] == "No discount"


def test_product_existence_check(tmp_path, payload):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    save_products_to_db(path_db, payload)

    example_url = "example.example"
    product_false_existence_status = product_existence_check(example_url, path_db)

    assert product_false_existence_status == False

    first_product_url = "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/"
    product_true_existence_status = product_existence_check(first_product_url, path_db)

    assert product_true_existence_status == True


def test_add_product_by_link(tmp_path, payload, monkeypatch):
    path_db = tmp_path / "data" / "products.db"

    db_init(path_db)

    monkeypatch.setattr(
        "price_monitor_api.main.get_html",
        lambda url: "html_1"
    )

    parser_response = {
        "name": "MECCHA CHAMELEON",
        "price": 6.15,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
        "created_at": "2026-07-22 19:14:15",
    }

    monkeypatch.setattr(
        "price_monitor_api.main.parse_page",
        lambda html_text: parser_response
    )

    product_link = "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/"
    added_product = add_product_by_link("product_link", path_db)

    assert added_product is not None

    expected_added_product = {
        "id": 1,
        "name": "MECCHA CHAMELEON",
        "price": 6.15,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
        "created_at": "2026-07-22 19:14:15",
    }

    assert added_product == expected_added_product

    check_all_products = get_all_products(path_db)

    assert check_all_products is not None

    expected_all_products = [
        {
            "id": 1,
            "name": "MECCHA CHAMELEON",
            "price": 6.15,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
            "created_at": "2026-07-22 19:14:15",
        },
    ]

    assert check_all_products == expected_all_products
