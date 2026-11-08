from flask import Blueprint, request

from controllers import pedido_controller

pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.post("/pedidos")
def criar_pedido():
    return pedido_controller.criar(request.get_json(silent=True))


@pedidos_bp.get("/pedidos")
def listar_todos_pedidos():
    return pedido_controller.listar_todos(request.args)


@pedidos_bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    return pedido_controller.listar_usuario(usuario_id, request.args)


@pedidos_bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    return pedido_controller.atualizar_status(
        pedido_id,
        request.get_json(silent=True),
    )
