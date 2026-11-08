import re

from utils.errors import ApiError
from utils.constants import (
    DEFAULT_PAGE_SIZE,
    MAX_DESCRIPTION_LENGTH,
    MAX_ITEMS_PER_ORDER,
    MAX_PAGE_SIZE,
    MAX_PRODUCT_NAME_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRODUCT_NAME_LENGTH,
    ORDER_STATUSES,
    PRODUCT_CATEGORIES,
    USER_TYPES,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _require_dict(payload) -> dict:
    if not isinstance(payload, dict):
        raise ApiError("Dados inválidos", 400)
    return payload


def _as_int(value, field: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise ApiError(f"{field} inválido", 400)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ApiError(f"{field} inválido", 400)
    if isinstance(value, float) and value != parsed:
        raise ApiError(f"{field} inválido", 400)
    if parsed < minimum:
        raise ApiError(f"{field} inválido", 400)
    return parsed


def _as_float(value, field: str, minimum: float = 0) -> float:
    if isinstance(value, bool):
        raise ApiError(f"{field} inválido", 400)
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ApiError(f"{field} inválido", 400)
    if parsed < minimum:
        raise ApiError(f"{field} inválido", 400)
    return parsed


def _as_optional_float(value, field: str):
    if value is None or value == "":
        return None
    return _as_float(value, field)


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ApiError("E-mail inválido", 400)
    return email


def validate_status(status: str) -> str:
    if status not in ORDER_STATUSES:
        raise ApiError("Status inválido", 400)
    return status


def validate_user_type(user_type: str) -> str:
    if user_type not in USER_TYPES:
        raise ApiError("Tipo de usuário inválido", 400)
    return user_type


def validate_product_payload(payload, partial: bool = False) -> dict:
    data = _require_dict(payload)
    result = {}

    if not partial or "nome" in data:
        nome = data.get("nome")
        if not isinstance(nome, str):
            raise ApiError("Nome é obrigatório", 400)
        nome = nome.strip()
        if len(nome) < MIN_PRODUCT_NAME_LENGTH:
            raise ApiError("Nome muito curto", 400)
        if len(nome) > MAX_PRODUCT_NAME_LENGTH:
            raise ApiError("Nome muito longo", 400)
        result["nome"] = nome

    if not partial or "preco" in data:
        result["preco"] = _as_float(data.get("preco"), "Preço", minimum=0)

    if not partial or "estoque" in data:
        result["estoque"] = _as_int(data.get("estoque"), "Estoque", minimum=0)

    if "descricao" in data:
        descricao = data.get("descricao") or ""
        if not isinstance(descricao, str):
            raise ApiError("Descrição inválida", 400)
        if len(descricao) > MAX_DESCRIPTION_LENGTH:
            raise ApiError("Descrição muito longa", 400)
        result["descricao"] = descricao.strip()
    elif not partial:
        result["descricao"] = ""

    if "categoria" in data:
        categoria = data.get("categoria")
        if categoria not in PRODUCT_CATEGORIES:
            raise ApiError(
                "Categoria inválida. Válidas: " + ", ".join(PRODUCT_CATEGORIES),
                400,
            )
        result["categoria"] = categoria
    elif not partial:
        result["categoria"] = "geral"

    return result


def validate_user_payload(payload, partial: bool = False) -> dict:
    data = _require_dict(payload)
    result = {}

    if not partial or "nome" in data:
        nome = data.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            raise ApiError("Nome é obrigatório", 400)
        result["nome"] = nome.strip()

    if not partial or "email" in data:
        email = data.get("email")
        if not isinstance(email, str) or not email.strip():
            raise ApiError("E-mail é obrigatório", 400)
        result["email"] = validate_email(email)

    if not partial or "senha" in data:
        senha = data.get("senha")
        if not isinstance(senha, str):
            raise ApiError("Senha é obrigatória", 400)
        if len(senha) < MIN_PASSWORD_LENGTH:
            raise ApiError(f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres", 400)
        result["senha"] = senha

    if "tipo" in data:
        result["tipo"] = validate_user_type(data.get("tipo"))
    elif not partial:
        result["tipo"] = "cliente"

    return result


def validate_login_payload(payload) -> dict:
    data = _require_dict(payload)
    email = data.get("email")
    senha = data.get("senha")
    if not isinstance(email, str) or not isinstance(senha, str):
        raise ApiError("E-mail e senha são obrigatórios", 400)
    if not email.strip() or not senha:
        raise ApiError("E-mail e senha são obrigatórios", 400)
    return {"email": validate_email(email), "senha": senha}


def validate_order_payload(payload) -> dict:
    data = _require_dict(payload)
    usuario_id = _as_int(data.get("usuario_id"), "Usuário", minimum=1)

    itens = data.get("itens")
    if not isinstance(itens, list) or not itens:
        raise ApiError("Pedido deve ter pelo menos 1 item", 400)
    if len(itens) > MAX_ITEMS_PER_ORDER:
        raise ApiError(f"Pedido excede o limite de {MAX_ITEMS_PER_ORDER} itens", 400)

    normalized = []
    for item in itens:
        if not isinstance(item, dict):
            raise ApiError("Item de pedido inválido", 400)
        normalized.append({
            "produto_id": _as_int(item.get("produto_id"), "Produto", minimum=1),
            "quantidade": _as_int(item.get("quantidade"), "Quantidade", minimum=1),
        })

    return {"usuario_id": usuario_id, "itens": normalized}


def parse_pagination(args) -> tuple[int, int]:
    page = _as_int(args.get("page", 1), "page", minimum=1)
    per_page = _as_int(args.get("per_page", DEFAULT_PAGE_SIZE), "per_page", minimum=1)
    return page, min(per_page, MAX_PAGE_SIZE)


def validate_search_filters(args) -> dict:
    termo = (args.get("q") or "").strip() or None
    categoria = args.get("categoria") or None
    if categoria and categoria not in PRODUCT_CATEGORIES:
        raise ApiError("Categoria inválida", 400)

    preco_min = _as_optional_float(args.get("preco_min"), "preco_min")
    preco_max = _as_optional_float(args.get("preco_max"), "preco_max")
    if preco_min is not None and preco_max is not None and preco_min > preco_max:
        raise ApiError("preco_min não pode ser maior que preco_max", 400)

    return {
        "termo": termo,
        "categoria": categoria,
        "preco_min": preco_min,
        "preco_max": preco_max,
    }
