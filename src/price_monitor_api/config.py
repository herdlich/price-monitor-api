from pathlib import Path

Path("data").mkdir(exist_ok=True)
DB_PATH = Path("data") / "products.db"
