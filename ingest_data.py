"""
Ingest generated e-commerce CSV datasets into a SQLite database with proper schema and relationships.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


DATA_FILES = {
    "customers": {
        "file": "customers.csv",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT,
                registration_date TEXT
            );
        """,
    },
    "products": {
        "file": "products.csv",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock_quantity INTEGER,
                supplier TEXT,
                description TEXT
            );
        """,
    },
    "orders": {
        "file": "orders.csv",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date TEXT,
                total_amount REAL,
                status TEXT,
                shipping_address TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
        """,
    },
    "order_items": {
        "file": "order_items.csv",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """,
    },
    "reviews": {
        "file": "reviews.csv",
        "create_sql": """
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                review_text TEXT,
                review_date TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
        """,
    },
}


def load_dataframe(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    return pd.read_csv(csv_path)


def create_tables(connection: sqlite3.Connection) -> None:
    with connection:
        for config in DATA_FILES.values():
            connection.execute(config["create_sql"])


def ingest_table(
    connection: sqlite3.Connection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> int:
    dataframe.to_sql(table_name, connection, if_exists="append", index=False)
    cursor = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    db_path = base_dir / "ecommerce.db"

    try:
        connection = sqlite3.connect(db_path)
        connection.execute("PRAGMA foreign_keys = ON;")
    except sqlite3.Error as exc:
        raise SystemExit(f"Failed to connect to database: {exc}") from exc

    try:
        create_tables(connection)

        for table_name, config in DATA_FILES.items():
            csv_path = data_dir / config["file"]
            try:
                df = load_dataframe(csv_path)
                row_count = ingest_table(connection, table_name, df)
                print(f"Loaded {row_count} rows into '{table_name}' table.")
            except (FileNotFoundError, pd.errors.ParserError) as exc:
                print(f"Skipping '{table_name}': {exc}")
            except sqlite3.IntegrityError as exc:
                print(f"Integrity error while loading '{table_name}': {exc}")
                raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()


