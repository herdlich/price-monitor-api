# Price Monitor API

A FastAPI-based REST API for tracking Steam game prices.

The service accepts a Steam Store product URL, downloads and parses the product page, stores the current product data in SQLite, and keeps a history of price changes. Price checks are triggered manually through the API.

## Features

- Add a Steam game by URL
- Validate HTTPS Steam Store links
- Extract and store the Steam `app_id`
- Prevent duplicate products by `app_id`
- Parse regular, discounted, and free-to-play products
- Handle Steam age-check pages
- List all tracked products
- Retrieve a product by its database ID
- Delete a product and its related price history
- Retrieve price history
- Manually refresh prices for all tracked products
- Store application logs
- Interactive OpenAPI documentation
- Automated tests with isolated temporary SQLite databases and local HTML fixtures

## Technology Stack

- Python 3.10+
- FastAPI
- Pydantic
- SQLite
- Requests
- Beautiful Soup
- Uvicorn
- Pytest

## Project Structure

```text
price-monitor-api/
├── data/                         # SQLite database
├── docs/                         # Additional project documentation
├── logs/                         # Application logs
├── src/
│   └── price_monitor_api/
│       ├── api.py                # FastAPI application and endpoints
│       ├── config.py             # Database path configuration
│       ├── database.py           # SQLite queries and schema
│       ├── exceptions.py         # Custom application exceptions
│       ├── main.py               # Business logic
│       ├── models.py             # Pydantic request/response models
│       └── parser.py             # Steam requests and HTML parsing
├── tests/
│   ├── api/
│   │   ├── test_history.py
│   │   ├── test_products.py
│   │   └── test_refresh_prices.py
│   ├── fixtures/
│   │   └── steam/                # Saved Steam HTML pages
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_main.py
│   └── test_parser.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/herdlich/price-monitor-api.git
cd price-monitor-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Run the command from the project root:

```bash
uvicorn src.price_monitor_api.api:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

The SQLite database is created automatically at:

```text
data/products.db
```

Application logs are written to:

```text
logs/price_monitor_api.log
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/products` | Add a Steam game |
| `GET` | `/products` | Get all tracked games |
| `GET` | `/products/{product_id}` | Get one game by database ID |
| `GET` | `/products/{product_id}/price-history` | Get a game's price history |
| `DELETE` | `/products/{product_id}` | Delete a game |
| `POST` | `/products/refresh-prices` | Check all tracked games and update changed prices |

## Usage Examples

### Add a product

```http
POST /products
Content-Type: application/json
```

```json
{
  "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/"
}
```

Example response:

```json
{
  "id": 1,
  "name": "RV There Yet?",
  "price": 7.79,
  "currency": "€",
  "discount": "No discount",
  "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/",
  "app_id": 3949040,
  "created_at": "2026-07-22 19:14:15"
}
```

Only HTTPS links from `store.steampowered.com` are accepted.

A duplicate Steam application returns `409 Conflict`:

```json
{
  "detail": {
    "code": "product_already_exists",
    "message": "Product \"RV There Yet?\" has already been added",
    "product_name": "RV There Yet?"
  }
}
```

### Get all products

```http
GET /products
```

Example response:

```json
[
  {
    "id": 1,
    "name": "RV There Yet?",
    "price": 7.79,
    "currency": "€",
    "discount": "No discount",
    "link": "https://store.steampowered.com/app/3949040/RV_There_Yet/",
    "app_id": 3949040,
    "created_at": "2026-07-22 19:14:15"
  }
]
```

### Get one product

```http
GET /products/1
```

A missing product returns `404 Not Found`.

### Get price history

```http
GET /products/1/price-history
```

Example response:

```json
[
  {
    "id": 1,
    "product_id": 1,
    "price": 7.79,
    "currency": "€",
    "discount": "No discount",
    "checked_at": "2026-07-22 19:14:15"
  }
]
```

An initial history record is created when the product is added. New records are added when the price, currency, or discount status changes.

### Delete a product

```http
DELETE /products/1
```

The deleted product is returned in the response. Its price history is removed automatically through the SQLite foreign-key cascade.

### Refresh prices

```http
POST /products/refresh-prices
```

The endpoint checks every stored Steam page. Only changed products are returned:

```json
[
  {
    "id": 2,
    "name": "Tainted Grail: The Fall of Avalon",
    "new_price": 19.99,
    "old_price": 21.99,
    "actual_currency": "€",
    "discount": "Discount"
  }
]
```

If no price data changed, the endpoint returns:

```json
[]
```

## How It Works

### Adding a product

```text
Steam URL
→ Pydantic URL validation
→ Steam app_id extraction
→ duplicate check
→ product page request
→ optional age-check handling
→ HTML parsing
→ SQLite product and history records
→ API response
```

### Refreshing prices

```text
Stored products
→ download current Steam pages
→ parse current values
→ compare price, currency, and discount
→ update changed products
→ append price-history records
→ return changed products
```

## Database

The application uses two SQLite tables.

### `products`

Stores the current product state:

- database ID
- Steam `app_id`
- name
- current price
- currency
- discount status
- canonical Steam URL
- creation timestamp

Both `link` and `app_id` are unique.

### `price_history`

Stores the initial price and later changes:

- history ID
- related product ID
- price
- currency
- discount status
- check timestamp

`price_history.product_id` references `products.id`. Deleting a product also deletes its history.

## Testing

Run all tests from the project root:

```bash
pytest
```

Verbose output:

```bash
pytest -v
```

The tests cover:

- Steam HTML parsing from local fixtures
- SQLite table creation and CRUD operations
- Product existence checks
- Product addition business logic
- Price refresh logic
- API product endpoints
- Price-history endpoint
- Manual price refresh endpoint

Tests do not depend on live Steam responses. Network operations are replaced with local HTML fixtures or mocked functions, and API tests use temporary SQLite databases created through `tmp_path`.

## Current Limitations

- Only Steam Store application URLs are supported.
- Price refresh is manual; there is no scheduler or background worker.
- There are no Telegram or email notifications.
- The service has no authentication or user accounts.
- SQLite is intended for local or small-scale use.
- The parser depends on Steam's current HTML structure and may require updates when the storefront markup changes.
- Regional restrictions or unusual Steam responses may prevent individual products from being parsed.
- Price history records successful additions and detected changes, not every unchanged check.
- Prices are currently stored as floating-point values.

## Possible Future Improvements

- Scheduled background price checks
- Telegram notifications
- User accounts and individual watchlists
- PostgreSQL and SQLAlchemy
- Alembic database migrations
- Docker support
- Deployment configuration
- Retry and rate-limit handling
- More detailed discount data
- Tests for additional Steam page variants

## License

No license has been specified yet.
