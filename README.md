# Vetty Backend

Vetty is a Flask-powered backend that exposes a RESTful API for a veterinary ecommerce and services platform. This repository contains only the server-side implementation; a separate React frontend will consume the API.

---

## Project Structure

- [`Pipfile`](Pipfile) — dependency manifest for Pipenv environment.
- [`server/app.py`](server/app.py) — development entry point that boots the Flask application.
- [`server/__init__.py`](server/__init__.py) — application factory wiring configuration, extensions, JWT callbacks, and resource registration.
- [`server/config.py`](server/config.py) — environment configuration helpers.
- [`server/extensions.py`](server/extensions.py) — singleton instances for SQLAlchemy, Marshmallow, JWT, CORS, and Migrate.
- [`server/models/`](server/models) — SQLAlchemy models for users, products, services, orders, bookings, reviews, and inventory movements.
- [`server/schemas/`](server/schemas) — Marshmallow schemas for request validation and serialization.
- [`server/resources/`](server/resources) — Flask-RESTful resources grouped by domain (auth, products, services, orders, bookings, reviews, inventory).
- [`server/auth/__init__.py`](server/auth/__init__.py) — JWT identity and error handler callbacks.
- [`server/seed.py`](server/seed.py) — script to reset and populate the database with Faker-driven sample data.
- [`migrations/`](migrations) — Alembic migration history generated via Flask-Migrate.
- [`docs/backend-requirements.md`](docs/backend-requirements.md) — backend MVP scope notes.
- [`plans/vetty-architecture-plan.md`](plans/vetty-architecture-plan.md) — high-level architecture and delivery plan.

---

## Environment Setup

1. **Install dependencies**
   ```bash
   pipenv install
   ```

2. **Activate virtual environment**
   ```bash
   pipenv shell
   ```

3. **Apply database migrations**
   ```bash
   pipenv run flask db upgrade
   ```

4. **Seed development data (optional)**
   ```bash
   pipenv run python -m server.seed
   ```

5. **Run the development server**
   ```bash
   pipenv run python server/app.py
   ```
   The API listens on `http://localhost:5555` by default.

---

## Configuration

The application reads environment variables from `.env` (loaded automatically by `python-dotenv`). Key variables:

- `FLASK_ENV` — set to `development`, `production`, or `testing`.
- `DATABASE_URL` — SQLAlchemy connection string (defaults to a SQLite file under `instance/app.db`).
- `SECRET_KEY` — Flask secret key.
- `JWT_SECRET_KEY` — signing key for JWT tokens.
- `LOG_LEVEL` — Python logging level (default `INFO`).

For local usage, copy `.env.example` (to be created by you) and adjust values.

---

## Database Models

The Alembic migration [`migrations/versions/0e2fa83b111d_create_initial_tables.py`](migrations/versions/0e2fa83b111d_create_initial_tables.py) generates these tables:

- `users` — application users (roles: customer, admin) with contact info and credential hashes.
- `products` — catalog entries with pricing, stock, SKU, creator, and soft-active flag.
- `services` — veterinary services offerings with duration and base price.
- `product_orders` — orders placed by customers with financial breakdown and status lifecycle.
- `order_items` — join table linking orders to products with quantity and captured pricing.
- `service_bookings` — scheduled appointments between customers and services, including status tracking.
- `reviews` — polymorphic feedback tied to either products or services.
- `inventory_movements` — audit log of manual or automated stock adjustments.

Model definitions live under [`server/models/`](server/models) and share timestamp mixins for `created_at`/`updated_at` fields.

---

## REST API Overview

All endpoints are prefixed with `/api`. Authentication-protected routes expect a Bearer JWT access token obtained via login.

### Authentication

- `POST /api/auth/register` — create a new customer account.
- `POST /api/auth/login` — obtain access and refresh tokens.
- `POST /api/auth/refresh` — swap refresh token for a new access token.
- `GET /api/auth/profile` — fetch current user profile (requires access token).
- `PATCH /api/auth/profile` — update name, phone, or default address.
- `POST /api/auth/password` — change current password.

### Catalog & Services

- `GET /api/products` — list products with optional `q` and `is_active` filters.
- `POST /api/products` — admin create product.
- `GET /api/products/<id>` — product details.
- `PATCH /api/products/<id>` — admin update.
- `DELETE /api/products/<id>` — admin delete.

- `GET /api/services` — list services with search.
- `POST /api/services` — admin create service.
- `GET /api/services/<id>` — service details.
- `PATCH /api/services/<id>` — admin update.
- `DELETE /api/services/<id>` — admin delete.

### Orders & Cart Checkout

- `GET /api/orders` — list orders for current user (admin sees all).
- `POST /api/orders` — submit a new order with line items; validates stock.
- `GET /api/orders/<id>` — retrieve order details (admin or owner).
- `PATCH /api/orders/<id>` — admin update status.

### Service Bookings

- `GET /api/bookings` — list bookings; admin vs customer scoping.
- `POST /api/bookings` — create a booking for a service.
- `GET /api/bookings/<id>` — fetch booking details (admin or owner).
- `PATCH /api/bookings/<id>` — admins approve/decline/complete; customers may cancel when pending/approved.

### Reviews

- `GET /api/reviews?product_id=&service_id=` — list reviews filtered by subject.
- `POST /api/reviews` — create review for a product or service post-fulfilment.
- `GET /api/reviews/<id>` — fetch review detail.
- `DELETE /api/reviews/<id>` — delete own review (admin can delete any).

### Inventory

- `GET /api/inventory-movements` — admin list with optional `product_id` filter.
- `POST /api/inventory-movements` — admin adjust stock with reason and references.

All write operations leverage Marshmallow validation defined under [`server/schemas/`](server/schemas).

---

## Validation & Error Handling

- Schemas enforce numeric ranges, string lengths, email format, payment reference patterns, and polymorphic review constraints.
- Global error handlers convert `marshmallow.ValidationError` to HTTP `422` responses and log `500` errors.
- Resource-level guards use JWT claims and helper utilities to check admin privileges.

---

## Testing Strategy (planned)

- Python `unittest` (pytest compatible) for unit and integration coverage of resources, models, and services.
- Factory Boy + Faker driven fixtures.
- Coverage goals focus on authentication flows, permission gates, order/booking lifecycle logic, and validation edge cases.

Test scaffolding will live beneath a future `tests/` directory.

---

## Deployment Notes

- Designed for deployment on Render or similar PaaS.
- Ensure environment variables are set in production (particularly secrets and database URL).
- Run migrations via `pipenv run flask db upgrade` during deploy.
- Seed script is for development only; avoid running on production data.

---

## API Reference for Frontend Integration

An OpenAPI/Swagger schema is not yet included. Frontend developers should reference this README alongside schema definitions in [`server/schemas`](server/schemas) and resource implementations in [`server/resources`](server/resources) for request/response contracts.

---

## Roadmap

- Add role-based admin dashboard metrics endpoints.
- Introduce payment confirmation webhooks (M-Pesa/Stripe) integration.
- Implement notification system (emails/SMS) for booking updates.
- Expand automated tests and CI workflows.
