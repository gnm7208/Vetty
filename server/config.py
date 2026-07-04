"""Configuration module for the Vetty backend."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "instance" / "app.db"


@dataclass()
class BaseConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION: tuple[str, ...] = ("headers", "cookies")
    JWT_COOKIE_SECURE: bool = False
    JWT_COOKIE_CSRF_PROTECT: bool = True
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # seconds
    CORS_RESOURCES: dict[str, dict[str, str]] = field(
        default_factory=lambda: {r"/api/*": {"origins": "*"}}
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


@dataclass()
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


@dataclass()
class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    JWT_COOKIE_SECURE: bool = False


@dataclass()
class ProductionConfig(BaseConfig):
    JWT_COOKIE_SECURE: bool = True


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name: str | None) -> type[BaseConfig]:
    """Return the config class based on the provided environment name."""

    env = config_name or os.getenv("FLASK_ENV", "development")
    return CONFIG_MAP.get(env, DevelopmentConfig)
