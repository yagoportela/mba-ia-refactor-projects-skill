from flask import current_app, jsonify

from utils.errors import ApiError
from models import usuario_model
from services.auth_service import create_token
from utils.validators import (
    parse_pagination,
    validate_login_payload,
    validate_user_payload,
)


def listar(args):
    page, per_page = parse_pagination(args)
    usuarios, total = usuario_model.list_all(page, per_page)
    return jsonify({
        "dados": usuarios,
        "sucesso": True,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }), 200


def buscar(usuario_id: int):
    usuario = usuario_model.get_by_id(usuario_id)
    if usuario is None:
        raise ApiError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar(payload):
    data = validate_user_payload(payload)
    if usuario_model.get_by_email(data["email"]) is not None:
        raise ApiError("E-mail já cadastrado", 409)
    usuario_id = usuario_model.create(
        nome=data["nome"],
        email=data["email"],
        senha=data["senha"],
        tipo=data["tipo"],
    )
    return jsonify({
        "dados": {"id": usuario_id},
        "sucesso": True,
    }), 201


def login(payload):
    data = validate_login_payload(payload)
    usuario = usuario_model.verify_credentials(data["email"], data["senha"])
    if usuario is None:
        raise ApiError("E-mail ou senha inválidos", 401)

    token = create_token(usuario["id"], current_app.config["SECRET_KEY"])
    return jsonify({
        "dados": {**usuario, "token": token},
        "sucesso": True,
        "mensagem": "Login OK",
    }), 200
