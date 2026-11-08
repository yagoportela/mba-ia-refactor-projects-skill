from flask import jsonify

from utils.errors import ApiError
from models import produto_model
from utils.validators import (
    parse_pagination,
    validate_product_payload,
    validate_search_filters,
)


def listar(args):
    page, per_page = parse_pagination(args)
    produtos, total = produto_model.list_all(page, per_page)
    return jsonify({
        "dados": produtos,
        "sucesso": True,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }), 200


def buscar(produto_id: int):
    produto = produto_model.get_by_id(produto_id)
    if produto is None:
        raise ApiError("Produto não encontrado", 404)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar(payload):
    data = validate_product_payload(payload)
    produto_id = produto_model.create(data)
    return jsonify({
        "dados": {"id": produto_id},
        "sucesso": True,
        "mensagem": "Produto criado",
    }), 201


def atualizar(produto_id: int, payload):
    if produto_model.get_by_id(produto_id) is None:
        raise ApiError("Produto não encontrado", 404)
    data = validate_product_payload(payload)
    produto_model.update(produto_id, data)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(produto_id: int):
    if not produto_model.delete(produto_id):
        raise ApiError("Produto não encontrado", 404)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos(args):
    filters = validate_search_filters(args)
    page, per_page = parse_pagination(args)
    produtos, total = produto_model.search(
        termo=filters["termo"],
        categoria=filters["categoria"],
        preco_min=filters["preco_min"],
        preco_max=filters["preco_max"],
        page=page,
        per_page=per_page,
    )
    return jsonify({
        "dados": produtos,
        "total": total,
        "sucesso": True,
        "meta": {"page": page, "per_page": per_page, "total": total},
    }), 200
