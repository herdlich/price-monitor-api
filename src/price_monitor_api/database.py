import sqlite3
from pathlib import Path
from contextlib import closing


def create_connection(db_file):
    connection = sqlite3.connect(db_file)

    connection.execute("""PRAGMA foreign_keys = ON""")

    return connection


def db_init(db_file):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                discount TEXT NOT NULL,
                link TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL,
                discount TEXT NOT NULL,
                checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (product_id)
                    REFERENCES products(id)
                    ON DELETE CASCADE
            ) 
            """)

            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_price_history_product
            ON price_history (product_id, checked_at)
            """)


def insert_price_history(cursor, product_id, data):
    cursor.execute(
        """
        INSERT INTO price_history (
            product_id,
            price,
            currency,
            discount
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            product_id,
            data["price"],
            data["currency"],
            data["discount"],
        ),
    )


def save_db(db_file, data):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO products (name, price, currency, discount, link, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                data["name"],
                data["price"],
                data["currency"],
                data["discount"],
                data["link"],
                data["created_at"]
            ))

            if cursor.rowcount == 1:
                product_id = cursor.lastrowid

                insert_price_history(cursor, product_id, data)

                return {
                    "id": product_id,
                    "name": data["name"],
                    "price": data["price"],
                    "currency": data["currency"],
                    "discount": data["discount"],
                    "link": data["link"],
                    "created_at": data["created_at"]
                }

        return {}


def get_all_products(db_file):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    connection.row_factory = sqlite3.Row

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
                SELECT id, name, price, currency, discount, link, created_at FROM products
            """)

            rows = cursor.fetchall()

    products = [dict(row) for row in rows]

    if not products:
        return []

    return products


def get_product_by_id(db_file, product_id):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)
    connection.row_factory = sqlite3.Row

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
            SELECT id, name, price, currency, discount, link, created_at
            FROM products
            WHERE id = ?
            """, (product_id,))

            row = cursor.fetchone()

    if row is None:
        return {}

    return dict(row)


def get_the_price_history_by_id(db_file, product_id):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    connection.row_factory = sqlite3.Row

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
                        SELECT id, product_id, price, currency, discount, checked_at FROM price_history
                        WHERE product_id = ?
                    """, (product_id,))

            rows = cursor.fetchall()

    if rows == []:
        return rows

    return [dict(row) for row in rows]


def delete_product_by_id(db_file, product_id):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute(
                """
                DELETE FROM products WHERE id = ?
                """, (product_id,))


def update_product(db_file, product_id, data):
    Path(db_file).parent.mkdir(exist_ok=True)

    connection = create_connection(db_file)

    with closing(connection) as db:
        with db:
            cursor = db.cursor()

            cursor.execute("""
                UPDATE products
                    SET price = ?, 
                    currency = ?,
                    discount = ?
                WHERE id = ?
            """, (
                data["price"],
                data["currency"],
                data["discount"],
                product_id,
            ))

            if cursor.rowcount == 0:
                raise ValueError(
                    f"Product with id={product_id} was not found"
                )

            insert_price_history(cursor, product_id, data)
