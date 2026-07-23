import re
import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)

page_url = "https://store.steampowered.com/app/2828860/The_Forever_Winter/"


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text

    except requests.RequestException as error:
        logger.error("Request error: %s\nURL: %s", error, url)
        return None


def parse_page(html_text):
    if not html_text:
        logger.error("HTML content is empty")
        return None

    soup = BS(html_text, "html.parser")

    name_element = soup.find("div", id="appHubAppName")

    if name_element is None:
        logger.warning("Name element is not found")
        return None

    price_element = soup.select_one(".discount_final_price")
    discount = "Discount"

    if price_element is None:
        price_element = soup.select_one(".game_purchase_price")
        discount = "No discount"

    if price_element is None:
        logger.warning("Price element is not found")
        return None

    canonical_element = soup.find("link", rel="canonical")
    if canonical_element is None or not canonical_element.get("href"):
        logger.error("Canonical link is not found")
        return None

    name = name_element.get_text(strip=True)

    price_text = price_element.get_text(" ", strip=True)

    if price_text.lower() == "free to play":
        clean_price = 0
    else:
        match = re.search(r"\d[\d.,\s\xa0]*", price_text)
        if match is None:
            logger.error("Could not parse price: %s",
                         price_text)
            return None

        clean_price = re.sub(r"[\s\xa0]+", "", match.group())
        clean_price = clean_price.replace(",", ".")

    try:
        price = float(clean_price)
    except ValueError:
        logger.error("Invalid price value: %s", clean_price)
        return None

    currency = re.sub(r"[\d\s\xa0.,]+", "", price_text).strip()
    if currency.lower() == "freetoplay":
        currency = ""

    return {
        "name": name,
        "price": price,
        "currency": currency,
        "discount": discount,
        "link": canonical_element["href"],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
