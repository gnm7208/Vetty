"""Seed script for populating development data."""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from faker import Faker

from server import create_app
from server.extensions import db
from server.models import (
    InventoryMovement,
    OrderItem,
    Product,
    ProductOrder,
    Review,
    Service,
    ServiceBooking,
    User,
)

fake = Faker()


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(name="Admin", email="admin@vetty.local", role="admin")
        admin.set_password("password123")

        customers = []
        for _ in range(5):
            customer = User(
                name=fake.name(),
                email=fake.unique.email(),
                role="customer",
                phone=fake.phone_number(),
                default_address=fake.address(),
            )
            customer.set_password("password123")
            customers.append(customer)

        db.session.add(admin)
        db.session.add_all(customers)
        db.session.commit()

        products = []
        for idx in range(10):
            product = Product(
                name=fake.word().title() + " Pet Product",
                description=fake.paragraph(nb_sentences=2),
                price_cents=random.randint(1500, 5000),
                stock_level=random.randint(10, 50),
                low_stock_threshold=5,
                sku=f"SKU-{idx:04d}",
                image_url=fake.image_url(),
                creator=admin,
            )
            products.append(product)

        services = []
        for idx in range(5):
            service = Service(
                title=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=3),
                base_price_cents=random.randint(3000, 8000),
                duration_minutes=random.choice([30, 45, 60, 90]),
                creator=admin,
            )
            services.append(service)

        db.session.add_all(products + services)
        db.session.commit()

        orders = []
        for _ in range(5):
            customer = random.choice(customers)
            order = ProductOrder(
                order_number=f"ORD{fake.unique.random_number(digits=6):06d}",
                status=random.choice(["pending", "approved", "dispatched", "delivered"]),
                delivery_address=customer.default_address or fake.address(),
                payment_reference=fake.bothify(text="??????????"),
                user=customer,
            )
            db.session.add(order)
            selected_products = random.sample(products, k=random.randint(1, 3))
            subtotal = 0
            for product in selected_products:
                quantity = random.randint(1, 3)
                line_total = product.price_cents * quantity
                subtotal += line_total
                order.items.append(
                    OrderItem(
                        product=product,
                        quantity=quantity,
                        unit_price_cents=product.price_cents,
                        line_total_cents=line_total,
                    )
                )
            order.subtotal_cents = subtotal
            order.tax_cents = int(subtotal * 0.1)
            order.delivery_fee_cents = 500
            order.total_cents = order.subtotal_cents + order.tax_cents + order.delivery_fee_cents
            orders.append(order)

        db.session.commit()

        bookings = []
        for _ in range(8):
            customer = random.choice(customers)
            service = random.choice(services)
            appointment_at = datetime.utcnow() + timedelta(days=random.randint(1, 14))
            booking = ServiceBooking(
                appointment_at=appointment_at,
                status=random.choice(["pending", "approved", "completed"]),
                pet_details=f"{fake.word()} the {fake.color_name()} pet",
                address=customer.default_address or fake.address(),
                notes=fake.sentence(),
                user=customer,
                service=service,
            )
            db.session.add(booking)

        db.session.commit()

        movements = []
        for product in products:
            delta = random.randint(-5, 5)
            if delta == 0:
                delta = 1
            movement = InventoryMovement(
                delta=delta,
                reason="Initial adjustment",
                product=product,
                actor=admin,
            )
            movements.append(movement)
            product.adjust_stock(delta)

        db.session.add_all(movements)
        db.session.commit()

        reviews = []
        for customer in customers:
            if random.choice([True, False]):
                product = random.choice(products)
                reviews.append(
                    Review(
                        rating=random.randint(3, 5),
                        comment=fake.sentence(),
                        user=customer,
                        product=product,
                    )
                )
            if random.choice([True, False]):
                service = random.choice(services)
                reviews.append(
                    Review(
                        rating=random.randint(3, 5),
                        comment=fake.sentence(),
                        user=customer,
                        service=service,
                    )
                )

        db.session.add_all(reviews)
        db.session.commit()

        print("Database seeded with sample data.")


if __name__ == "__main__":
    seed()
