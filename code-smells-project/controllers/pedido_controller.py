from flask import jsonify

from utils.errors import ApiError
from models import pedido_model, usuario_model
from services.notification_service import NotificationService
from utils.validators import (
    parse_pagination,
    validate_order_payload,
    validate_status,
)

notifications = NotificationService()


def criar(payload):
    data = validate_order_payload(payload)

    if usuario_model.get_by_id(data["usuario_id"]) is None:
        raise ApiError("Usuário não encontrado", 404)

    resultado = pedido_model.create(data["usuario_id"], data["itens"])
    notifications.order_created(resultado["pedido_id"], data["usuario_id"])

    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_usuario(usuario_id: int, args):
    page, per_page = parse_pagination(args)
    pedidos, total = pedido_model.list_by_usuario(usuario_id, page, per_page)
    return jsonify({
        "dados": pedidos,
        "sucesso": True,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }), 200


def listar_todos(args):
    page, per_page = parse_pagination(args)
    pedidos, total = pedido_model.list_all(page, per_page)
    return jsonify({
        "dados": pedidos,
        "sucesso": True,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }), 200


def atualizar_status(pedido_id: int, payload):
    if not isinstance(payload, dict):
        raise ApiError("Dados inválidos", 400)
    status = validate_status(payload.get("status"))
    if not pedido_model.update_status(pedido_id, status):
        raise ApiError("Pedido não encontrado", 404)

    notifications.order_status_changed(pedido_id, status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
