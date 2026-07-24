from pathlib import Path

from price_monitor_api.parser import parse_page


def test_parse_regular_product_page():
    current_dir = Path(__file__)
    html_path = current_dir.parent / "fixtures" / "steam" / "regular_product.html"

    with open(html_path, "r", encoding="utf-8") as file:
        html_text = file.read()

    parsed_product = parse_page(html_text)

    assert parsed_product is not None

    expected_parsed_product = {
        "name": "RV There Yet?",
        "price": 7.79,
        "currency": "€",
        "discount": "No discount",
        "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/",
    }

    parsed_product.pop("created_at")

    assert parsed_product == expected_parsed_product
