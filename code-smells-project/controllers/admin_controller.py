from flask import jsonify

from database import reset_db
from utils.errors import ApiError


def reset_database():
    reset_db()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def execute_query():
    raise ApiError(
        "Endpoint removido por segurança. Use os relatórios específicos.",
        410,
    )
