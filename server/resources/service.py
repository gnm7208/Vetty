"""Service resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from ..extensions import db
from ..models import Service
from ..schemas import ServiceSchema, ServiceWriteSchema
from .utils import get_current_user, require_admin

service_schema = ServiceSchema()
service_write_schema = ServiceWriteSchema()


class ServiceListResource(Resource):
    def get(self):
        query = Service.query
        is_active = request.args.get("is_active")
        search = request.args.get("q")

        if is_active is not None:
            query = query.filter(Service.is_active == (is_active.lower() == "true"))
        if search:
            like_pattern = f"%{search.strip()}%"
            query = query.filter(Service.title.ilike(like_pattern))

        services = query.order_by(Service.created_at.desc()).all()
        return service_schema.dump(services, many=True), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        require_admin(current_user)

        payload = request.get_json() or {}
        data = service_write_schema.load(payload)

        service = Service(
            title=data["title"],
            description=data.get("description"),
            base_price_cents=data["base_price_cents"],
            duration_minutes=data["duration_minutes"],
            is_active=data.get("is_active", True),
            creator=current_user,
        )

        db.session.add(service)
        db.session.commit()
        return service_schema.dump(service), HTTPStatus.CREATED


class ServiceDetailResource(Resource):
    def get(self, service_id: int):
        service = Service.query.get_or_404(service_id)
        return service_schema.dump(service), HTTPStatus.OK

    @jwt_required()
    def patch(self, service_id: int):
        current_user = get_current_user()
        require_admin(current_user)

        service = Service.query.get_or_404(service_id)
        payload = request.get_json() or {}
        data = service_write_schema.load(payload, partial=True)

        for field in [
            "title",
            "description",
            "base_price_cents",
            "duration_minutes",
            "is_active",
        ]:
            if field in data:
                setattr(service, field, data[field])

        db.session.commit()
        return service_schema.dump(service), HTTPStatus.OK

    @jwt_required()
    def delete(self, service_id: int):
        current_user = get_current_user()
        require_admin(current_user)

        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        return {"message": "Service deleted"}, HTTPStatus.NO_CONTENT
