"""Service booking resources."""

from __future__ import annotations

from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource, abort

from ..extensions import db
from ..models import Service, ServiceBooking
from ..schemas import ServiceBookingSchema, ServiceBookingWriteSchema
from .utils import get_current_user, require_admin

booking_schema = ServiceBookingSchema()
bookings_schema = ServiceBookingSchema(many=True)
booking_write_schema = ServiceBookingWriteSchema()


class BookingListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        if current_user.role == "admin":
            bookings = ServiceBooking.query.order_by(ServiceBooking.created_at.desc()).all()
        else:
            bookings = (
                ServiceBooking.query.filter_by(user_id=current_user.id)
                .order_by(ServiceBooking.created_at.desc())
                .all()
            )
        return bookings_schema.dump(bookings), HTTPStatus.OK

    @jwt_required()
    def post(self):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        payload = request.get_json() or {}
        data = booking_write_schema.load(payload)

        service = Service.query.filter_by(id=data["service_id"], is_active=True).first()
        if not service:
            abort(HTTPStatus.NOT_FOUND, message="Service not found")

        booking = ServiceBooking(
            appointment_at=data["appointment_at"],
            pet_details=data["pet_details"],
            address=data["address"],
            notes=data.get("notes"),
            status="pending",
            user=current_user,
            service=service,
        )

        db.session.add(booking)
        db.session.commit()
        return booking_schema.dump(booking), HTTPStatus.CREATED


class BookingDetailResource(Resource):
    @jwt_required()
    def get(self, booking_id: int):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        booking = ServiceBooking.query.get_or_404(booking_id)
        if current_user.role != "admin" and booking.user_id != current_user.id:
            abort(HTTPStatus.FORBIDDEN, message="Access denied")

        return booking_schema.dump(booking), HTTPStatus.OK

    @jwt_required()
    def patch(self, booking_id: int):
        current_user = get_current_user()
        if not current_user:
            return {"error": "User not found"}, HTTPStatus.NOT_FOUND

        booking = ServiceBooking.query.get_or_404(booking_id)

        payload = request.get_json() or {}
        allowed_statuses = {"pending", "approved", "declined", "completed", "cancelled"}
        requested_status = payload.get("status")

        if requested_status and requested_status not in allowed_statuses:
            abort(HTTPStatus.BAD_REQUEST, message="Invalid status")

        if current_user.role == "admin":
            if requested_status and requested_status != booking.status:
                booking.status = requested_status
        else:
            if requested_status and requested_status not in {"cancelled"}:
                abort(HTTPStatus.FORBIDDEN, message="Customers can only cancel bookings")
            if requested_status == "cancelled" and booking.status in {"pending", "approved"}:
                booking.status = "cancelled"
            elif requested_status == "cancelled":
                abort(HTTPStatus.BAD_REQUEST, message="Cannot cancel this booking")

        db.session.commit()
        return booking_schema.dump(booking), HTTPStatus.OK
