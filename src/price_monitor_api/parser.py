import re
import requests
import logging
from datetime import datetime
from urllib.parse import urlsplit
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)

page_url = "https://store.steampowered.com/app/2828860/The_Forever_Winter/"


def extract_app_id(url: str):
    parsed_url = urlsplit(url)
    parts = parsed_url.path.strip("/").split("/")

    try:
        app_index = parts.index("app")
        app_id = parts[app_index + 1]
    except (ValueError, IndexError):
        return None

    if app_id.isdigit():
        return app_id

    return None


def extract_session_id(html_text: str) -> str:
    match = re.search(r'g_sessionID\s*=\s*"([^"]+)"', html_text)
    if match is None:
        logger.warning("Steam session ID is not found")
        raise ValueError("Steam session ID is not found")

    return match.group(1)


def is_age_check_page(response: requests.Response) -> bool:
    return (
            "/agecheck/" in response.url
            or 'id="ageYear"' in response.text
            or "CheckAgeGateSubmit" in response.text
    )


def pass_age_check(
        session: requests.Session,
        age_response: requests.Response,
        app_id: str,
) -> requests.Response:
    session_id = extract_session_id(age_response.text)

    verification_response = session.post(
        f"https://store.steampowered.com/agecheckset/app/{app_id}/",
        data={
            "sessionid": session_id,
            "ageDay": "1",
            "ageMonth": "January",
            "ageYear": "1990"
        },
        timeout=10
    )

    verification_response.raise_for_status()
    verification_result = verification_response.json()

    if verification_result.get("success") != 1:
        logger.warning("Age verification failed: %s",
                       verification_result)
        raise RuntimeError(f"Age verification failed: {verification_result}")

    session.cookies.set(
        "wants_mature_content",
        "1",
        domain="store.steampowered.com",
        path=f"/app/{app_id}"
    )

    product_url = f"https://store.steampowered.com/app/{app_id}/"

    return session.get(product_url, timeout=10)


def get_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        with requests.Session() as session:
            session.headers.update(headers)

            response = session.get(url, timeout=10)
            response.raise_for_status()

            if is_age_check_page(response):
                logger.info("Age verification required. Final URL: %s",
                            response.url)

                app_id = extract_app_id(url)
                if app_id is None:
                    logger.warning("Could not extract app ID: %s",
                                   response.url)

                    raise ValueError(f"Could not extract app ID: {response.url}")

                response = pass_age_check(
                    session=session,
                    age_response=response,
                    app_id=str(app_id)
                )
                response.raise_for_status()

                if is_age_check_page(response):
                    raise RuntimeError("Steam returned the agecheck page again")

            return response.text

    except (requests.RequestException, ValueError, RuntimeError) as error:
        logger.error("Page loading error: %s\nURL: %s", error, url)
        return None


def parse_price_value(price_text: str) -> float | None:
    text = price_text.strip()

    if text.casefold() in ["free to play"]:
        return float(0)

    match = re.search(r"\d(?:[\d.,\s\xa0]*\d)?", text)
    if match is None:
        logger.error("Could not find price: %s", price_text)
        return None

    raw_price = re.sub(r"[\s\xa0]+", "", match.group())

    has_comma = "," in raw_price
    has_dot = "." in raw_price
    decimal_separator = None

    if has_comma and has_dot:
        decimal_separator = (
            "," if raw_price.rfind(",") > raw_price.rfind(".") else "."
        )

    elif has_comma or has_dot:
        separator = "," if has_comma else "."
        fraction_length = len(raw_price.rsplit(separator, 1)[1])

        if fraction_length in (1, 2):
            decimal_separator = separator

    if decimal_separator:
        integer_part, fractional_part = raw_price.rsplit(
            decimal_separator,
            1
        )

        integer_part = re.sub(r"[.,]", "", integer_part)
        normalized_price = f"{integer_part}.{fractional_part}"

    else:
        normalized_price = re.sub(r"[.,]", "", raw_price)

    try:
        return float(normalized_price)

    except ValueError as e:
        logger.warning("Invalid price value: %s, normalized: %s",
                       raw_price, normalized_price)

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

    price = parse_price_value(price_text)

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
