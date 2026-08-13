from datetime import date, timedelta
from decimal import Decimal
import random

from app.database.connection import SessionLocal
from app.database.models import (
    Customer,
    Product,
    Order,
    OrderItem,
    Payment,
)


CITIES = ["Pune", "Mumbai", "Bengaluru", "Delhi", "Hyderabad"]

SEGMENTS = ["regular", "premium", "business"]

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home",
    "Books",
    "Sports",
]

PRODUCT_NAMES = {
    "Electronics": [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "Bluetooth Speaker",
        "USB-C Hub",
        "Webcam",
    ],
    "Clothing": [
        "T-Shirt",
        "Jeans",
        "Jacket",
        "Sneakers",
        "Hoodie",
    ],
    "Home": [
        "Desk Lamp",
        "Water Bottle",
        "Coffee Mug",
        "Storage Box",
        "Wall Clock",
    ],
    "Books": [
        "Python Basics",
        "Data Science Handbook",
        "SQL Fundamentals",
        "Machine Learning Guide",
        "Statistics Essentials",
    ],
    "Sports": [
        "Yoga Mat",
        "Football",
        "Badminton Racket",
        "Dumbbells",
        "Skipping Rope",
    ],
}

ORDER_STATUSES = [
    "completed",
    "completed",
    "completed",
    "shipped",
    "cancelled",
]

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
]


def seed_database() -> None:
    random.seed(42)

    db = SessionLocal()

    try:
        # Avoid inserting the same seed data twice.
        if db.query(Customer).first():
            print("Database already contains data. Skipping seed.")
            return

        customers = []

        for i in range(1, 51):
            customer = Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                city=random.choice(CITIES),
                customer_segment=random.choice(SEGMENTS),
            )

            db.add(customer)
            customers.append(customer)

        products = []

        for category, names in PRODUCT_NAMES.items():
            for name in names:
                product = Product(
                    product_name=name,
                    category=category,
                    unit_price=Decimal(
                        str(
                            round(
                                random.uniform(200, 5000),
                                2,
                            )
                        )
                    ),
                )

                db.add(product)
                products.append(product)

        db.flush()

        today = date.today()

        orders = []

        for _ in range(200):
            customer = random.choice(customers)

            order_date = today - timedelta(
                days=random.randint(0, 365)
            )

            status = random.choice(ORDER_STATUSES)

            order = Order(
                customer_id=customer.customer_id,
                order_date=order_date,
                status=status,
                total_amount=Decimal("0.00"),
            )

            db.add(order)
            db.flush()

            number_of_items = random.randint(1, 4)

            selected_products = random.sample(
                products,
                number_of_items,
            )

            total_amount = Decimal("0.00")

            for product in selected_products:
                quantity = random.randint(1, 3)

                line_total = (
                    product.unit_price * quantity
                )

                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=product.unit_price,
                )

                db.add(order_item)

                total_amount += line_total

            order.total_amount = total_amount

            orders.append(order)

            if status != "cancelled":
                payment_status = (
                    "completed"
                    if status in ["completed", "shipped"]
                    else "pending"
                )

                payment = Payment(
                    order_id=order.order_id,
                    payment_date=order_date,
                    payment_method=random.choice(
                        PAYMENT_METHODS
                    ),
                    amount=total_amount,
                    status=payment_status,
                )

                db.add(payment)

        db.commit()

        print("Synthetic data inserted successfully.")
        print(f"Customers: {len(customers)}")
        print(f"Products: {len(products)}")
        print(f"Orders: {len(orders)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()