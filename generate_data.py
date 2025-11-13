"""
Script to generate synthetic e-commerce datasets as CSV files.
"""

from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from faker import Faker


def daterange_within_years(years: int = 2) -> datetime:
    """Return a random datetime within the past `years` years."""
    now = datetime.now()
    start = now - timedelta(days=365 * years)
    delta = now - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def generate_customers(fake: Faker, count: int) -> List[Dict[str, str]]:
    customers = []
    for customer_id in range(1, count + 1):
        profile = fake.simple_profile()
        address = fake.street_address()
        city = fake.city()
        state = fake.state_abbr()
        zip_code = fake.postcode()
        phone = fake.phone_number()

        customers.append(
            {
                "customer_id": str(customer_id),
                "first_name": profile["name"].split(" ")[0],
                "last_name": profile["name"].split(" ")[-1],
                "email": profile["mail"],
                "phone": phone,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "registration_date": daterange_within_years().strftime("%Y-%m-%d"),
            }
        )
    return customers


def generate_products(fake: Faker, count: int) -> List[Dict[str, str]]:
    categories = [
        "Electronics",
        "Home & Kitchen",
        "Sports",
        "Beauty",
        "Books",
        "Toys",
        "Clothing",
        "Health",
        "Automotive",
        "Office Supplies",
    ]
    suppliers = [
        "Northwind Traders",
        "Globex Corporation",
        "Initech",
        "Umbrella Supplies",
        "Soylent Corp",
        "Acme Wholesale",
    ]

    products = []
    for product_id in range(1, count + 1):
        category = random.choice(categories)
        price = round(random.uniform(5, 500), 2)
        products.append(
            {
                "product_id": str(product_id),
                "product_name": fake.catch_phrase(),
                "category": category,
                "price": f"{price:.2f}",
                "stock_quantity": str(random.randint(0, 500)),
                "supplier": random.choice(suppliers),
                "description": fake.sentence(nb_words=12),
            }
        )
    return products


def distribute_items(num_orders: int, total_items: int, min_per_order: int = 1, max_per_order: int = 5) -> List[int]:
    """Create a distribution of items per order summing to total_items."""
    items_per_order = [min_per_order] * num_orders
    remaining = total_items - num_orders * min_per_order

    order_indices = list(range(num_orders))
    while remaining > 0:
        random.shuffle(order_indices)
        for idx in order_indices:
            if remaining <= 0:
                break
            if items_per_order[idx] < max_per_order:
                items_per_order[idx] += 1
                remaining -= 1
        # Safety to avoid infinite loops if constraints impossible
        if all(count == max_per_order for count in items_per_order):
            break
    if sum(items_per_order) != total_items:
        raise ValueError("Unable to distribute order items with given constraints.")
    return items_per_order


def generate_orders_and_items(
    fake: Faker,
    customers: List[Dict[str, str]],
    products: List[Dict[str, str]],
    num_orders: int,
    total_order_items: int,
) -> tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

    orders: List[Dict[str, str]] = []
    order_items: List[Dict[str, str]] = []

    items_distribution = distribute_items(num_orders, total_order_items)

    product_lookup = {product["product_id"]: product for product in products}

    order_item_counter = 1
    for order_id in range(1, num_orders + 1):
        customer = random.choice(customers)
        num_items = items_distribution[order_id - 1]
        order_date = daterange_within_years()

        shipping_address = f"{fake.street_address()}, {fake.city()}, {fake.state_abbr()} {fake.postcode()}"

        order_subtotal = 0.0
        used_products = set()
        for _ in range(num_items):
            product = random.choice(products)
            # Avoid duplicate products in a single order when possible
            retries = 0
            while product["product_id"] in used_products and retries < 5:
                product = random.choice(products)
                retries += 1
            used_products.add(product["product_id"])

            quantity = random.randint(1, 4)
            unit_price = float(product["price"])
            subtotal = unit_price * quantity
            order_subtotal += subtotal

            order_items.append(
                {
                    "order_item_id": str(order_item_counter),
                    "order_id": str(order_id),
                    "product_id": product["product_id"],
                    "quantity": str(quantity),
                    "unit_price": f"{unit_price:.2f}",
                    "subtotal": f"{subtotal:.2f}",
                }
            )
            order_item_counter += 1

        total_amount = round(order_subtotal, 2)
        orders.append(
            {
                "order_id": str(order_id),
                "customer_id": customer["customer_id"],
                "order_date": order_date.strftime("%Y-%m-%d"),
                "total_amount": f"{total_amount:.2f}",
                "status": random.choices(
                    population=statuses, weights=[0.1, 0.2, 0.35, 0.3, 0.05], k=1
                )[0],
                "shipping_address": shipping_address,
            }
        )

    return orders, order_items


def generate_reviews(
    fake: Faker,
    customers: List[Dict[str, str]],
    products: List[Dict[str, str]],
    count: int,
) -> List[Dict[str, str]]:
    reviews = []
    for review_id in range(1, count + 1):
        customer = random.choice(customers)
        product = random.choice(products)
        rating = random.randint(1, 5)
        review_length = random.randint(12, 25)
        reviews.append(
            {
                "review_id": str(review_id),
                "product_id": product["product_id"],
                "customer_id": customer["customer_id"],
                "rating": str(rating),
                "review_text": fake.sentence(nb_words=review_length),
                "review_date": daterange_within_years().strftime("%Y-%m-%d"),
            }
        )
    return reviews


def write_csv(file_path: Path, rows: List[Dict[str, str]], headers: List[str]) -> None:
    with file_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    random.seed(42)
    fake = Faker()
    fake.seed_instance(42)

    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(fake, 100)
    products = generate_products(fake, 50)
    orders, order_items = generate_orders_and_items(fake, customers, products, 200, 400)
    reviews = generate_reviews(fake, customers, products, 150)

    write_csv(
        data_dir / "customers.csv",
        customers,
        [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "registration_date",
        ],
    )

    write_csv(
        data_dir / "products.csv",
        products,
        [
            "product_id",
            "product_name",
            "category",
            "price",
            "stock_quantity",
            "supplier",
            "description",
        ],
    )

    write_csv(
        data_dir / "orders.csv",
        orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "total_amount",
            "status",
            "shipping_address",
        ],
    )

    write_csv(
        data_dir / "order_items.csv",
        order_items,
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "subtotal",
        ],
    )

    write_csv(
        data_dir / "reviews.csv",
        reviews,
        [
            "review_id",
            "product_id",
            "customer_id",
            "rating",
            "review_text",
            "review_date",
        ],
    )

    print(f"Data generated in {data_dir}")


if __name__ == "__main__":
    main()


