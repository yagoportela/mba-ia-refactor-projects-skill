import hmac
from functools import wraps

from flask import current_app, request

from utils.errors import ApiError


def require_admin_token(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN", "")
        if not expected:
            raise ApiError("Admin desabilitado: configure ADMIN_TOKEN", 403)

        provided = request.headers.get("X-Admin-Token", "")
        if not hmac.compare_digest(provided, expected):
            raise ApiError("Não autorizado", 401)

        return view(*args, **kwargs)

    return wrapped
