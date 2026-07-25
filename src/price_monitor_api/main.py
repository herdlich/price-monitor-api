from .database import save_db, get_all_products, update_product
from .parser import get_html, parse_page
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def setup_logging():
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        filename="logs/price_monitor_api.log",
        level=logging.INFO,
        encoding="utf-8",
        format="[%(asctime)s] - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def check_actual_products(db_file):
    products_list = get_all_products(db_file)

    changed_products = []

    if not products_list:
        logger.warning("Database is empty")
        return False

    for product in products_list:
        html_text = get_html(product["link"])
        if not html_text:
            logger.warning("Could not download product: %s",
                           product["link"])
            continue

        actual_product = parse_page(html_text)

        if actual_product is None:
            logger.warning("Could not parse product: %s",
                           product["link"])
            continue

        price_changed = product["price"] != actual_product["price"]
        currency_changed = product["currency"] != actual_product["currency"]
        discount_changed = product["discount"] != actual_product["discount"]

        if price_changed or currency_changed or discount_changed:
            update_product(
                db_file,
                product["id"],
                actual_product
            )

            actual_product_response = {
                "id": product["id"],
                "name": actual_product["name"],
                "new_price": actual_product["price"],
                "old_price": product["price"],
                "actual_currency": actual_product["currency"],
                "discount": actual_product["discount"],
            }

            changed_products.append(actual_product_response)

            logger.info(
                "Price changed \"%s\": %s %s -> %s %s",
                product["name"],
                product["price"],
                product["currency"],
                actual_product["price"],
                actual_product["currency"]
            )

    return changed_products


def product_existence_check(url, db_file):
    products = get_all_products(db_file)

    for product in products:
        if product["link"] == url:
            logger.warning('The product "%s" has already been added', product["name"])
            return True

    return False


def add_product_by_link(page_url, db_file):
    setup_logging()

    flag_existence = product_existence_check(page_url, db_file)
    if flag_existence is True:
        return None

    html_text = get_html(page_url)
    if not html_text:
        logger.error("Product page could not be loaded")
        return None

    product_dict = parse_page(html_text)
    if not product_dict:
        logger.error("Product page could not be parsed")
        return None

    saved_product = save_db(db_file, product_dict)

    if saved_product:
        logger.info("Product saved: \"%s\", id=%s",
                    product_dict["name"],
                    saved_product["id"], )
        return saved_product

    else:
        logger.info("Product \"%s\" was not saved",
                    product_dict["name"], )
        return None
