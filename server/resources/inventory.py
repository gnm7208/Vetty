"""Inventory management resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from ..extensions import db
from ..models import InventoryMovement, Product
from ..schemas import InventoryMovementSchema, InventoryMovementWriteSchema
from .utils import get_current_user, require_admin

inventory_schema = InventoryMovementSchema()
inventory_list_schema = InventoryMovementSchema(many=True)
inventory_write_schema = InventoryMovementWriteSchema()


class InventoryMovementListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_current_user()
        require_admin(current_user)

        product_id = request.args.get("product_id", type=int)
        query = InventoryMovement.query
        if product_id:
            query = query.filter_by(product_id=product_id)

        movements = query.order_by(InventoryMovement.created_at.desc()).limit(200).all()
        return inventory_list_schema.dump(movements), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        require_admin(current_user)

        payload = request.get_json() or {}
        data = inventory_write_schema.load(payload)

        product = Product.query.get(data["product_id"])
        if not product:
            abort(HTTPStatus.NOT_FOUND, message="Product not found")

        product.adjust_stock(data["delta"])

        movement = InventoryMovement(
            delta=data["delta"],
            reason=data["reason"],
            reference_type=data.get("reference_type"),
            reference_id=data.get("reference_id"),
            notes=data.get("notes"),
            product=product,
            actor=current_user,
        )

        db.session.add(movement)
        db.session.commit()
        return inventory_schema.dump(movement), HTTPStatus.CREATED
