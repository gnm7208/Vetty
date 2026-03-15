"""Product resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from ..extensions import db
from ..models import Product
from ..schemas import ProductSchema, ProductWriteSchema
from .utils import get_current_user, require_admin

product_schema = ProductSchema()
product_write_schema = ProductWriteSchema()


class ProductListResource(Resource):
    def get(self):
        query = Product.query
        is_active = request.args.get("is_active")
        search = request.args.get("q")

        if is_active is not None:
            query = query.filter(Product.is_active == (is_active.lower() == "true"))
        if search:
            like_pattern = f"%{search.strip()}%"
            query = query.filter(Product.name.ilike(like_pattern))

        products = query.order_by(Product.created_at.desc()).all()
        return product_schema.dump(products, many=True), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        require_admin(current_user)

        payload = request.get_json() or {}
        data = product_write_schema.load(payload)

        if Product.query.filter_by(sku=data["sku"]).first():
            abort(HTTPStatus.CONFLICT, message="SKU already exists")

        product = Product(
            name=data["name"],
            description=data.get("description"),
            price_cents=data["price_cents"],
            stock_level=data["stock_level"],
            low_stock_threshold=data["low_stock_threshold"],
            sku=data["sku"],
            image_url=data.get("image_url"),
            is_active=data.get("is_active", True),
            creator=current_user,
        )

        db.session.add(product)
        db.session.commit()
        return product_schema.dump(product), HTTPStatus.CREATED


class ProductDetailResource(Resource):
    def get(self, product_id: int):
        product = Product.query.get_or_404(product_id)
        return product_schema.dump(product), HTTPStatus.OK

    @jwt_required()
    def patch(self, product_id: int):
        current_user = get_current_user()
        require_admin(current_user)

        product = Product.query.get_or_404(product_id)
        payload = request.get_json() or {}
        data = product_write_schema.load(payload, partial=True)

        if "sku" in data and data["sku"] != product.sku:
            if Product.query.filter_by(sku=data["sku"]).first():
                abort(HTTPStatus.CONFLICT, message="SKU already exists")
            product.sku = data["sku"]

        for field in [
            "name",
            "description",
            "price_cents",
            "stock_level",
            "low_stock_threshold",
            "image_url",
            "is_active",
        ]:
            if field in data:
                setattr(product, field, data[field])

        db.session.commit()
        return product_schema.dump(product), HTTPStatus.OK

    @jwt_required()
    def delete(self, product_id: int):
        current_user = get_current_user()
        require_admin(current_user)

        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted"}, HTTPStatus.NO_CONTENT
