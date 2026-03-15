"""Review resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from ..extensions import db
from ..models import Product, Review, Service
from ..schemas import ReviewSchema, ReviewWriteSchema
from .utils import get_current_user

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
review_write_schema = ReviewWriteSchema()


class ReviewListResource(Resource):
    def get(self):
        product_id = request.args.get("product_id", type=int)
        service_id = request.args.get("service_id", type=int)

        query = Review.query
        if product_id:
            query = query.filter_by(product_id=product_id)
        if service_id:
            query = query.filter_by(service_id=service_id)

        reviews = query.order_by(Review.created_at.desc()).all()
        return reviews_schema.dump(reviews), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        payload = request.get_json() or {}
        data = review_write_schema.load(payload)

        if data.get("product_id"):
            product = Product.query.filter_by(id=data["product_id"], is_active=True).first()
            if not product:
                abort(HTTPStatus.NOT_FOUND, message="Product not found")
        if data.get("service_id"):
            service = Service.query.filter_by(id=data["service_id"], is_active=True).first()
            if not service:
                abort(HTTPStatus.NOT_FOUND, message="Service not found")

        review = Review(
            rating=data["rating"],
            comment=data.get("comment"),
            product_id=data.get("product_id"),
            service_id=data.get("service_id"),
            user=current_user,
        )

        db.session.add(review)
        db.session.commit()
        return review_schema.dump(review), HTTPStatus.CREATED


class ReviewDetailResource(Resource):
    def get(self, review_id: int):
        review = Review.query.get_or_404(review_id)
        return review_schema.dump(review), HTTPStatus.OK

    @jwt_required()
    def delete(self, review_id: int):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        review = Review.query.get_or_404(review_id)
        if review.user_id != current_user.id and current_user.role != "admin":
            abort(HTTPStatus.FORBIDDEN, message="Not authorised to delete this review")

        db.session.delete(review)
        db.session.commit()
        return {"message": "Review deleted"}, HTTPStatus.NO_CONTENT
