from flask import current_app, g, request

from utils.errors import ApiError
from services.auth_service import verify_token

PUBLIC_PATHS = {"/", "/health", "/login"}


def register_auth(app):
    @app.before_request
    def enforce_auth():
        if not app.config.get("AUTH_REQUIRED"):
            return None
        if request.method == "OPTIONS" or request.path in PUBLIC_PATHS:
            return None

        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            raise ApiError("Não autorizado", 401)

        payload = verify_token(header[7:].strip(), current_app.config["SECRET_KEY"])
        if payload is None:
            raise ApiError("Token inválido ou expirado", 401)

        g.current_user_id = payload["user_id"]
        return None
