import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _cors_origins(debug: bool) -> list[str]:
    configured = [
        origin.strip()
        for origin in os.environ.get("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if configured:
        return configured
    return ["*"] if debug else []


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "loja.db"))
    DEBUG = _bool_env("DEBUG", False)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
    APP_VERSION = "1.0.0"
    CORS_ORIGINS = _cors_origins(DEBUG)
