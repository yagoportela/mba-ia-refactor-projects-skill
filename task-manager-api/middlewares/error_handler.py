from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import ApiError


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": error.description}), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro inesperado", exc_info=error)
        return jsonify({"error": "Erro interno"}), 500
