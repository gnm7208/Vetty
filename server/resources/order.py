"""Order resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from ..extensions import db
from ..models import OrderItem, Product, ProductOrder
from ..schemas import OrderItemSchema, ProductOrderSchema, ProductOrderWriteSchema
from .utils import get_current_user, require_admin

order_schema = ProductOrderSchema()
orders_schema = ProductOrderSchema(many=True)
order_write_schema = ProductOrderWriteSchema()
order_item_schema = OrderItemSchema()


class OrderListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        role = current_user.role
        if role == "admin":
            orders = ProductOrder.query.order_by(ProductOrder.created_at.desc()).all()
        else:
            orders = (
                ProductOrder.query.filter_by(user_id=current_user.id)
                .order_by(ProductOrder.created_at.desc())
                .all()
            )
        return orders_schema.dump(orders), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        payload = request.get_json() or {}
        data = order_write_schema.load(payload)

        if not data["items"]:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, message="Order requires at least one item")

        order_items = []
        for item_data in data["items"]:
            product = Product.query.filter_by(id=item_data["product_id"], is_active=True).first()
            if not product:
                abort(HTTPStatus.NOT_FOUND, message=f"Product {item_data['product_id']} not found")
            if product.stock_level < item_data["quantity"]:
                abort(HTTPStatus.BAD_REQUEST, message=f"Insufficient stock for product {product.sku}")

            order_item = OrderItem(
                product=product,
                quantity=item_data["quantity"],
                unit_price_cents=item_data["unit_price_cents"],
                line_total_cents=item_data["line_total_cents"],
            )
            order_items.append(order_item)

        order = ProductOrder(
            order_number=_generate_order_number(),
            status="pending",
            subtotal_cents=data["subtotal_cents"],
            tax_cents=data.get("tax_cents", 0),
            delivery_fee_cents=data.get("delivery_fee_cents", 0),
            total_cents=data["total_cents"],
            delivery_address=data["delivery_address"],
            payment_reference=data["payment_reference"],
            user=current_user,
        )
        order.items = order_items

        db.session.add(order)
        db.session.commit()

        for order_item in order_items:
            order_item.product.adjust_stock(-order_item.quantity)

        db.session.commit()
        return order_schema.dump(order), HTTPStatus.CREATED


class OrderDetailResource(Resource):
    @jwt_required()
    def get(self, order_id: int):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        order = ProductOrder.query.get_or_404(order_id)
        if current_user.role != "admin" and order.user_id != current_user.id:
            abort(HTTPStatus.FORBIDDEN, message="Access denied")

        return order_schema.dump(order), HTTPStatus.OK

    @jwt_required()
    def patch(self, order_id: int):
        current_user = get_current_user()
        require_admin(current_user)

        order = ProductOrder.query.get_or_404(order_id)
        payload = request.get_json() or {}

        allowed_statuses = {
            "pending",
            "approved",
            "dispatched",
            "delivered",
            "cancelled",
        }

        new_status = payload.get("status")
        if new_status and new_status not in allowed_statuses:
            abort(HTTPStatus.BAD_REQUEST, message="Invalid status")

        if new_status and new_status != order.status:
            order.status = new_status

        db.session.commit()
        return order_schema.dump(order), HTTPStatus.OK


def _generate_order_number() -> str:
    last_order = ProductOrder.query.order_by(ProductOrder.id.desc()).first()
    next_id = (last_order.id + 1) if last_order else 1
    return f"ORD{next_id:06d}"
