from flask import current_app, jsonify

from models import health_model


def health():
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": health_model.counts(),
        "versao": current_app.config.get("APP_VERSION", "1.0.0"),
    }), 200
