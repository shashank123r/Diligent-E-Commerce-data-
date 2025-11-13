"""
Analyze the e-commerce SQLite database and export key insights to CSV files.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def ensure_output_dir(base_dir: Path) -> Path:
    output_dir = base_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_query(connection: sqlite3.Connection, query: str, params: tuple | None = None) -> pd.DataFrame:
    return pd.read_sql_query(query, connection, params=params)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "ecommerce.db"

    if not db_path.exists():
        raise SystemExit(f"Database not found at {db_path}. Run ingest_data.py first.")

    output_dir = ensure_output_dir(base_dir)

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON;")

    queries = {
        "top_customers": """
            SELECT
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                c.email,
                COUNT(o.order_id) AS orders_count,
                ROUND(SUM(o.total_amount), 2) AS total_spent
            FROM customers c
            JOIN orders o ON o.customer_id = c.customer_id
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT 10;
        """,
        "product_performance": """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                ROUND(COALESCE(SUM(oi.subtotal), 0), 2) AS total_revenue,
                COALESCE(SUM(oi.quantity), 0) AS units_sold,
                ROUND(AVG(r.rating), 2) AS average_rating
            FROM products p
            LEFT JOIN order_items oi ON oi.product_id = p.product_id
            LEFT JOIN reviews r ON r.product_id = p.product_id
            GROUP BY p.product_id
            ORDER BY total_revenue DESC;
        """,
        "monthly_sales": """
            SELECT
                strftime('%Y-%m', o.order_date) AS month,
                ROUND(SUM(o.total_amount), 2) AS total_revenue,
                COUNT(o.order_id) AS orders_count
            FROM orders o
            WHERE o.order_date >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month;
        """,
        "category_analysis": """
            SELECT
                p.category,
                ROUND(SUM(oi.subtotal), 2) AS total_revenue,
                COUNT(DISTINCT o.order_id) AS orders_count,
                ROUND(SUM(oi.subtotal) / NULLIF(COUNT(DISTINCT o.order_id), 0), 2) AS average_order_value
            FROM order_items oi
            JOIN products p ON p.product_id = oi.product_id
            JOIN orders o ON o.order_id = oi.order_id
            GROUP BY p.category
            ORDER BY total_revenue DESC;
        """,
        "customer_reviews": """
            SELECT
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                COUNT(r.review_id) AS reviews_count,
                COUNT(DISTINCT r.product_id) AS products_reviewed,
                ROUND(AVG(r.rating), 2) AS average_rating
            FROM customers c
            LEFT JOIN reviews r ON r.customer_id = c.customer_id
            GROUP BY c.customer_id
            HAVING reviews_count > 0
            ORDER BY reviews_count DESC, average_rating DESC;
        """,
    }

    results: dict[str, pd.DataFrame] = {}

    try:
        for name, query in queries.items():
            df = run_query(connection, query)
            results[name] = df
            output_file = output_dir / f"{name}.csv"
            df.to_csv(output_file, index=False)
            print(f"Wrote {len(df)} rows to {output_file.name}")

        # Console summary
        total_revenue_df = run_query(connection, "SELECT ROUND(SUM(total_amount), 2) AS total_revenue FROM orders;")
        total_revenue = total_revenue_df["total_revenue"].iloc[0] if not total_revenue_df.empty else 0.0

        top_customer = results["top_customers"].iloc[0] if not results["top_customers"].empty else None
        best_product = results["product_performance"].iloc[0] if not results["product_performance"].empty else None

        print("\nSummary Insights")
        print("----------------")
        print(f"Total revenue: ${total_revenue:,}")
        if top_customer is not None:
            print(
                f"Top customer: {top_customer['customer_name']} (${top_customer['total_spent']:,} across {top_customer['orders_count']} orders)"
            )
        if best_product is not None:
            print(
                f"Best-selling product: {best_product['product_name']} (Revenue ${best_product['total_revenue']:,}, Units sold {best_product['units_sold']})"
            )
        if not results["monthly_sales"].empty:
            recent_month = results["monthly_sales"].iloc[-1]
            print(
                f"Most recent month ({recent_month['month']}): Revenue ${recent_month['total_revenue']:,} across {recent_month['orders_count']} orders"
            )
    finally:
        connection.close()


if __name__ == "__main__":
    main()


