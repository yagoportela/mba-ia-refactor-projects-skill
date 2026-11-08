from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import ApiError


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        payload = {"erro": error.message, "sucesso": False}
        if error.details:
            payload["detalhes"] = error.details
        return jsonify(payload), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "erro": error.description,
            "sucesso": False,
        }), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro inesperado", exc_info=error)
        return jsonify({
            "erro": "Erro interno do servidor",
            "sucesso": False,
        }), 500
