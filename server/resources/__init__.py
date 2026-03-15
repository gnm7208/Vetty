"""Resource registration for the Vetty API."""

from __future__ import annotations

from flask_restful import Api

from .auth import (
    LoginResource,
    PasswordChangeResource,
    ProfileResource,
    RegisterResource,
    TokenRefreshResource,
)
from .booking import BookingDetailResource, BookingListResource
from .order import OrderDetailResource, OrderListResource
from .product import ProductDetailResource, ProductListResource
from .review import ReviewDetailResource, ReviewListResource
from .service import ServiceDetailResource, ServiceListResource


def register_resources(api: Api) -> None:
    """Register resource endpoints with the provided API instance."""
    api.add_resource(RegisterResource, "/auth/register")
    api.add_resource(LoginResource, "/auth/login")
    api.add_resource(TokenRefreshResource, "/auth/refresh")
    api.add_resource(ProfileResource, "/auth/profile")
    api.add_resource(PasswordChangeResource, "/auth/password")
    api.add_resource(ProductListResource, "/products")
    api.add_resource(ProductDetailResource, "/products/<int:product_id>")
    api.add_resource(ServiceListResource, "/services")
    api.add_resource(ServiceDetailResource, "/services/<int:service_id>")
    api.add_resource(OrderListResource, "/orders")
    api.add_resource(OrderDetailResource, "/orders/<int:order_id>")
    api.add_resource(BookingListResource, "/bookings")
    api.add_resource(BookingDetailResource, "/bookings/<int:booking_id>")
    api.add_resource(ReviewListResource, "/reviews")
    api.add_resource(ReviewDetailResource, "/reviews/<int:review_id>")
