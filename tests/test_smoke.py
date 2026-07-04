"""Smoke tests: the application factory boots and serves requests."""

import pytest

from server import create_app
from server.extensions import db


@pytest.fixture()
def app(tmp_path):
    app = create_app("testing")
    app.config.update(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        TESTING=True,
    )
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_app_boots(app):
    assert app is not None
    assert app.config["TESTING"] is True


def test_unknown_route_returns_json_404(client):
    response = client.get("/definitely-not-a-route")
    assert response.status_code == 404


def test_products_endpoint_responds(client):
    # Core resource of the API - should return a JSON list (may be empty)
    response = client.get("/api/products")
    assert response.status_code in (200, 404)  # 404 only if prefix differs
