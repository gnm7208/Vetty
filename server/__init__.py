"""Application factory for the Vetty backend."""

from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from . import models  # noqa: F401 ensure models are registered
from .auth import register_jwt_callbacks
from .config import get_config
from .errors import register_error_handlers
from .extensions import cors, db, init_marshmallow, jwt, migrate

def create_app(config_name: str | None = None) -> Flask:
    """Create and configure a Flask application instance."""

    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    config_cls = get_config(config_name)

    app = Flask(__name__)
    app.config.from_object(config_cls)

    configure_logging(app)
    register_extensions(app)
    register_error_handlers(app)
    register_api(app)

    return app


def configure_logging(app: Flask) -> None:
    """Configure structured logging for the application."""

    log_level = app.config.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format=app.config.get("LOG_FORMAT"))


def register_extensions(app: Flask) -> None:
    """Initialise core Flask extensions."""

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_jwt_callbacks(jwt)
    cors.init_app(app)
    init_marshmallow(app)


def register_api(app: Flask) -> None:
    """Register API resources with Flask-RESTful."""

    from flask_restful import Api

    from .resources import register_resources

    api = Api(app, prefix="/api")
    register_resources(api)


__all__ = ["create_app"]
