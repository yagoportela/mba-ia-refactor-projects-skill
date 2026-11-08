from flask import Blueprint, request

from controllers import produto_controller

produtos_bp = Blueprint("produtos", __name__)


@produtos_bp.get("/produtos")
def listar_produtos():
    return produto_controller.listar(request.args)


@produtos_bp.get("/produtos/busca")
def buscar_produtos():
    return produto_controller.buscar_produtos(request.args)


@produtos_bp.get("/produtos/<int:produto_id>")
def buscar_produto(produto_id):
    return produto_controller.buscar(produto_id)


@produtos_bp.post("/produtos")
def criar_produto():
    return produto_controller.criar(request.get_json(silent=True))


@produtos_bp.put("/produtos/<int:produto_id>")
def atualizar_produto(produto_id):
    return produto_controller.atualizar(produto_id, request.get_json(silent=True))


@produtos_bp.delete("/produtos/<int:produto_id>")
def deletar_produto(produto_id):
    return produto_controller.deletar(produto_id)
