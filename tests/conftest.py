from fastapi.testclient import TestClient
from price_monitor_api.database import db_init
from price_monitor_api.api import app
import pytest


@pytest.fixture()
def client(monkeypatch, tmp_path):
    path_db = tmp_path / "data" / "products.db"

    monkeypatch.setattr(
        "price_monitor_api.api.DB_PATH",
        path_db
    )

    monkeypatch.setattr(
        "price_monitor_api.main.DB_PATH",
        path_db
    )

    db_init(path_db)

    return TestClient(app)


@pytest.fixture()
def payload():
    payload = [
        {
            "name": "MECCHA CHAMELEON",
            "price": 6.15,
            "currency": "€",
            "discount": "No discount",
            "link": "https://store.steampowered.com/app/4704690/MECCHA_CHAMELEON/",
            "created_at": "2026-07-22 19:14:15"
        },
        {
            "name": "Tainted Grail: The Fall of Avalon",
            "price": 21.99,
            "currency": "€",
            "discount": "Discount",
            "link": "https://store.steampowered.com/app/1466060/Tainted_Grail_The_Fall_of_Avalon/",
            "created_at": "2026-07-23 12:28:08"
        }
    ]

    return payload
