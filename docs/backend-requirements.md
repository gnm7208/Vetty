# Vetty Backend MVP Requirements

## Functional Scope

### Authentication & Authorization
- Email/password registration for pet owners and admin managers.
- JWT-based login issuing access and refresh tokens.
- Role-based guards restricting administrative endpoints to admins only.

### Product Catalog Management
- Admins can create, update, activate/deactivate, and delete products.
- Products expose name, description, pricing, SKU, stock level, and image URL.
- Public endpoints for listing products with optional filters and retrieving single product detail.

### Service Catalog & Booking
- Admins can maintain service offerings (title, description, base price, duration, active flag).
- Customers can request service bookings specifying appointment datetime, pet details, address, and optional notes.
- Booking lifecycle statuses: `pending`, `approved`, `declined`, `completed`, `cancelled`.
- Admin endpoints to approve/decline/update bookings.

### Orders & Cart Checkout
- Customers submit product orders containing line items with quantity and pricing snapshot.
- System calculates order totals (subtotal, tax, delivery fee, total).
- Stores delivery address and payment reference metadata (e.g., M-Pesa transaction code).
- Admins can update order statuses: `pending`, `approved`, `dispatched`, `delivered`, `cancelled`.

### Reviews & Feedback
- Customers who completed orders or bookings can post ratings (1-5) and comments for products or services.
- Public read endpoints surface reviews associated with each product or service.

### Inventory Oversight (MVP)
- Product stock decremented on approved orders; admins can adjust stock levels.
- Low-stock threshold flagging (e.g., when stock < configurable minimum) exposed via admin endpoint.

## Non-Functional Requirements
- RESTful API built with Flask-RESTful following JSON-based request/response conventions.
- PostgreSQL primary datastore accessed via SQLAlchemy ORM.
- Marshmallow schemas enforce request validation (data types, formats, constraints).
- CORS enabled for future React frontend consumption.
- Comprehensive logging for auditing admin actions and failed authentication attempts.
- Automated testing covering critical business flows (auth, orders, bookings, reviews).
- Configuration via environment variables for database URLs, JWT secrets, and CORS origins.
- Deployable on Render (or similar) with Gunicorn entrypoint and managed migrations.

## Out of Scope for Backend Delivery
- Frontend UI implementation (handled separately).
- Realtime websockets or push notifications (future enhancement).
- Payment gateway integration beyond storing payment reference metadata.
- Background job processing (e.g., email reminders) unless APIs need to expose scheduling hooks.
