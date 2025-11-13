# E-Commerce Data Analytics Pipeline

## Overview
This project simulates an end-to-end e-commerce analytics workflow. It generates realistic synthetic datasets, ingests them into a relational database, performs analytical queries, and produces both tabular exports and a polished HTML report summarizing key business insights.

## Project Structure
```
├── data/                     # Generated CSV datasets (created by generate_data.py)
├── output/                   # Analytical CSVs and HTML report (created by analyze_data.py & generate_report.py)
├── analyze_data.py           # Runs SQL analytics and exports aggregated CSVs
├── generate_data.py          # Produces synthetic e-commerce CSV datasets
├── generate_report.py        # Builds the HTML analytics report from output CSVs
├── ingest_data.py            # Creates SQLite schema and ingests generated data
├── ecommerce.db              # SQLite database populated via ingest_data.py (created at runtime)
└── README.md                 # Project documentation (this file)
```
> Note: `data/`, `output/`, and `ecommerce.db` are created when the scripts are executed.

## Prerequisites
- Python 3.9+ (tested on Python 3.11)
- Recommended: virtual environment (venv, Poetry, etc.)
- Python libraries:
  - `faker`
  - `pandas`

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-data-analysis
   ```
2. **Create and activate a virtual environment (optional but recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate          # macOS / Linux
   .\.venv\Scripts\activate           # Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt    # If provided
   ```
   or install directly:
   ```bash
   pip install faker pandas
   ```

## Execution Workflow
Run the scripts in the following order to reproduce the full analytics pipeline:

1. **Generate synthetic data**
   ```bash
   python generate_data.py
   ```
   Creates five CSV files in `data/`.

2. **Ingest data into SQLite**
   ```bash
   python ingest_data.py
   ```
   Builds `ecommerce.db`, creates tables, and loads the CSV data.

3. **Run analytical queries**
   ```bash
   python analyze_data.py
   ```
   Executes SQL queries against `ecommerce.db`, storing results in `output/` and printing headline metrics.

4. **Generate HTML report**
   ```bash
   python generate_report.py
   ```
   Reads the analytical CSVs and produces `output/report.html`, a styled executive report.

## Data Files & Table Schemas
| CSV / Table          | Columns                                                                                 | Description |
|----------------------|-----------------------------------------------------------------------------------------|-------------|
| `customers.csv` / `customers` | `customer_id`, `first_name`, `last_name`, `email`, `phone`, `address`, `city`, `state`, `zip_code`, `registration_date` | Customer master data with registration dates within the last two years. |
| `products.csv` / `products`   | `product_id`, `product_name`, `category`, `price`, `stock_quantity`, `supplier`, `description`                      | Product catalog across multiple retail categories. |
| `orders.csv` / `orders`       | `order_id`, `customer_id`, `order_date`, `total_amount`, `status`, `shipping_address`                               | Order headers linked to customers; statuses mirror real fulfillment stages. |
| `order_items.csv` / `order_items` | `order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`, `subtotal`                                 | Line-level order details linking orders to products. |
| `reviews.csv` / `reviews`     | `review_id`, `product_id`, `customer_id`, `rating`, `review_text`, `review_date`                                   | Product reviews with customer attribution and 1–5 star ratings. |

**Foreign key relationships**
- `orders.customer_id → customers.customer_id`
- `order_items.order_id → orders.order_id`
- `order_items.product_id → products.product_id`
- `reviews.customer_id → customers.customer_id`
- `reviews.product_id → products.product_id`

## Analytical Queries
| Output CSV                  | Purpose |
|-----------------------------|---------|
| `top_customers.csv`         | Ranks the top 10 customers by lifetime spend, including order counts and contact details. |
| `product_performance.csv`   | Summarizes revenue, units sold, and average rating per product. |
| `monthly_sales.csv`         | Tracks monthly revenue and order volume for the last 12 months. |
| `category_analysis.csv`     | Evaluates category-level performance by revenue, order counts, and average order value. |
| `customer_reviews.csv`      | Profiles customer engagement with review counts, coverage, and average ratings. |

## Sample Insights
- **Total Revenue:** Generated from the synthetic dataset—reported in script output and the HTML dashboard.
- **Top Customer:** Identified by highest cumulative spend across orders.
- **Best-Selling Product:** Product with leading revenue contribution, including units sold and average rating.
- **Recent Monthly Trend:** Latest month’s revenue and order volume highlighted in both CLI summary and report.
- **Customer Satisfaction:** Average rating and most active reviewers computed from `reviews`.

These insights refresh each time you regenerate the data; they emulate realistic patterns for testing analytics workflows.

## Technologies Used
- Python (data generation, ingestion, analytics, reporting)
- SQLite (relational data storage)
- pandas (data manipulation, SQL result handling)
- Faker (synthetic data generation)
- HTML & CSS (report presentation)

## Author
- **Name:** Shashank R (example; replace with actual author if different)
- **Contact:** shashank@example.com
- **GitHub:** [github.com/username](https://github.com/shashank123r)

Feel free to update the author section with your real contact information. Contributions and enhancements are welcome!


