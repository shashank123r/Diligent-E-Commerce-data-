"""
Generate an HTML report summarizing e-commerce analytics from precomputed CSV outputs.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV not found: {path}")
    df = pd.read_csv(path)
    return df


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def df_to_html_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if max_rows is not None:
        df = df.head(max_rows)
    return (
        df.to_html(index=False, classes="table", border=0, justify="center")
        .replace('class="dataframe table"', 'class="table"')
    )


def build_monthly_chart(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No monthly sales data available.</p>"

    max_revenue = df["total_revenue"].max()
    if max_revenue <= 0:
        return "<p>No revenue recorded for the selected period.</p>"

    lines = []
    for _, row in df.iterrows():
        bar_length = max(1, int((row["total_revenue"] / max_revenue) * 40))
        bar = "#" * bar_length
        lines.append(f"{row['month']}: {bar} {format_currency(row['total_revenue'])}")

    chart = "\n".join(lines)
    return f"<pre class='chart'>{chart}</pre>"


def gather_summary_metrics(
    datasets: Dict[str, pd.DataFrame],
    customers_path: Path,
) -> Dict[str, float | int | str]:
    monthly_sales = datasets["monthly_sales"]
    top_customers = datasets["top_customers"]
    product_performance = datasets["product_performance"]

    total_revenue = float(monthly_sales["total_revenue"].sum()) if not monthly_sales.empty else 0.0
    total_orders = int(monthly_sales["orders_count"].sum()) if not monthly_sales.empty else 0
    average_order_value = total_revenue / total_orders if total_orders else 0.0

    total_customers = None
    if customers_path.exists():
        total_customers = len(pd.read_csv(customers_path))
    elif not top_customers.empty:
        total_customers = top_customers["customer_id"].nunique()
    else:
        total_customers = 0

    top_customer_name = top_customers.iloc[0]["customer_name"] if not top_customers.empty else "N/A"
    best_product_name = (
        product_performance.iloc[0]["product_name"] if not product_performance.empty else "N/A"
    )

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "average_order_value": average_order_value,
        "total_customers": total_customers,
        "top_customer_name": top_customer_name,
        "best_product_name": best_product_name,
    }


def build_customer_satisfaction_section(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No customer review data available.</p>"

    total_reviews = int(df["reviews_count"].sum())
    weighted_rating_sum = (df["average_rating"] * df["reviews_count"]).sum()
    average_rating = weighted_rating_sum / total_reviews if total_reviews else 0.0

    most_active = df.sort_values(["reviews_count", "average_rating"], ascending=[False, False]).iloc[0]

    stats_html = f"""
    <ul class="metrics">
        <li><strong>Total Reviews:</strong> {total_reviews}</li>
        <li><strong>Average Rating:</strong> {average_rating:.2f} / 5</li>
        <li><strong>Most Active Reviewer:</strong> {most_active['customer_name']} ({int(most_active['reviews_count'])} reviews)</li>
    </ul>
    """

    table_html = df_to_html_table(
        df.rename(
            columns={
                "reviews_count": "Reviews Count",
                "products_reviewed": "Products Reviewed",
                "average_rating": "Average Rating",
            }
        ).round({"Average Rating": 2}),
        max_rows=10,
    )
    return stats_html + table_html


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "output"
    if not output_dir.exists():
        raise SystemExit(f"Output directory not found at {output_dir}. Run analyze_data.py first.")

    csv_files = {
        "top_customers": output_dir / "top_customers.csv",
        "product_performance": output_dir / "product_performance.csv",
        "monthly_sales": output_dir / "monthly_sales.csv",
        "category_analysis": output_dir / "category_analysis.csv",
        "customer_reviews": output_dir / "customer_reviews.csv",
    }

    datasets = {name: load_csv(path) for name, path in csv_files.items()}

    summary = gather_summary_metrics(datasets, base_dir / "data" / "customers.csv")

    report_date = datetime.now().strftime("%B %d, %Y")

    top_customers_table = df_to_html_table(
        datasets["top_customers"].rename(
            columns={
                "customer_name": "Customer",
                "email": "Email",
                "orders_count": "Orders",
                "total_spent": "Total Spent",
            }
        ).assign(**{"Total Spent": lambda df: df["Total Spent"].map(format_currency)}),
        max_rows=5,
    )

    top_products_table = df_to_html_table(
        datasets["product_performance"]
        .rename(
            columns={
                "product_name": "Product",
                "category": "Category",
                "total_revenue": "Total Revenue",
                "units_sold": "Units Sold",
                "average_rating": "Average Rating",
            }
        )
        .assign(**{"Total Revenue": lambda df: df["Total Revenue"].map(format_currency)})
        .round({"Average Rating": 2}),
        max_rows=5,
    )

    category_table = df_to_html_table(
        datasets["category_analysis"]
        .rename(
            columns={
                "category": "Category",
                "total_revenue": "Total Revenue",
                "orders_count": "Orders",
                "average_order_value": "Average Order Value",
            }
        )
        .assign(
            **{
                "Total Revenue": lambda df: df["Total Revenue"].map(format_currency),
                "Average Order Value": lambda df: df["Average Order Value"].map(format_currency),
            }
        ),
    )

    monthly_chart = build_monthly_chart(datasets["monthly_sales"])
    customer_satisfaction = build_customer_satisfaction_section(datasets["customer_reviews"])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>E-Commerce Analytics Report</title>
    <style>
        body {{
            font-family: "Segoe UI", Arial, sans-serif;
            margin: 0;
            background-color: #f6f8fb;
            color: #1f2933;
        }}
        header {{
            background-color: #1f4b99;
            color: white;
            padding: 30px 40px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        }}
        header h1 {{
            margin: 0;
            font-size: 32px;
            letter-spacing: 0.5px;
        }}
        header p {{
            margin: 8px 0 0;
            font-size: 15px;
        }}
        main {{
            padding: 30px 40px 60px;
        }}
        section {{
            margin-bottom: 36px;
            background-color: white;
            border-radius: 10px;
            padding: 24px 28px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }}
        section h2 {{
            margin-top: 0;
            font-size: 22px;
            color: #16315c;
        }}
        .metrics {{
            list-style: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 16px 40px;
            margin: 0;
        }}
        .metrics li {{
            font-size: 16px;
        }}
        .metrics strong {{
            color: #0f265c;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }}
        .summary-card {{
            background-color: #1f4b99;
            color: white;
            padding: 18px 22px;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.18);
        }}
        .summary-card h3 {{
            margin: 0 0 6px;
            font-size: 14px;
            letter-spacing: 1px;
            text-transform: uppercase;
            opacity: 0.85;
        }}
        .summary-card p {{
            margin: 0;
            font-size: 20px;
            font-weight: 600;
        }}
        table.table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 16px;
        }}
        table.table th, table.table td {{
            border: 1px solid #d0d7e2;
            padding: 10px 12px;
            text-align: left;
        }}
        table.table th {{
            background-color: #eef2fb;
            font-weight: 600;
        }}
        table.table tr:nth-child(every) {{
            background-color: #fafbff;
        }}
        .chart {{
            background-color: #0e1d38;
            color: #f6f8fb;
            padding: 16px;
            border-radius: 8px;
            font-family: "Cascadia Code", "Courier New", monospace;
            font-size: 14px;
            overflow-x: auto;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            font-size: 13px;
            color: #5a6d8a;
        }}
    </style>
</head>
<body>
    <header>
        <h1>E-Commerce Analytics Report</h1>
        <p>Generated on {report_date}</p>
    </header>
    <main>
        <section>
            <h2>Executive Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Total Revenue</h3>
                    <p>{format_currency(summary['total_revenue'])}</p>
                </div>
                <div class="summary-card">
                    <h3>Total Orders</h3>
                    <p>{summary['total_orders']:,}</p>
                </div>
                <div class="summary-card">
                    <h3>Total Customers</h3>
                    <p>{summary['total_customers']:,}</p>
                </div>
                <div class="summary-card">
                    <h3>Average Order Value</h3>
                    <p>{format_currency(summary['average_order_value'])}</p>
                </div>
            </div>
            <ul class="metrics" style="margin-top:24px;">
                <li><strong>Top Customer:</strong> {summary['top_customer_name']}</li>
                <li><strong>Best-Selling Product:</strong> {summary['best_product_name']}</li>
            </ul>
        </section>

        <section>
            <h2>Top Customers</h2>
            {top_customers_table}
        </section>

        <section>
            <h2>Top Products</h2>
            {top_products_table}
        </section>

        <section>
            <h2>Monthly Sales Trend</h2>
            {monthly_chart}
        </section>

        <section>
            <h2>Category Performance</h2>
            {category_table}
        </section>

        <section>
            <h2>Customer Satisfaction</h2>
            {customer_satisfaction}
        </section>
    </main>
    <footer>
        &copy; {datetime.now().year} E-Commerce Analytics
    </footer>
</body>
</html>
"""

    report_path = output_dir / "report.html"
    report_path.write_text(html_content, encoding="utf-8")
    print(f"Report generated at {report_path}")


if __name__ == "__main__":
    main()


