import re
from datetime import datetime

from utils.errors import ApiError
from utils.constants import (
    DEFAULT_COLOR,
    DEFAULT_PAGE_SIZE,
    DEFAULT_PRIORITY,
    MAX_PAGE_SIZE,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


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


def _optional_id(value, field: str):
    if value is None or value == "":
        return None
    return _as_int(value, field, minimum=1)


def validate_id(value, field: str = "id") -> int:
    return _as_int(value, field, minimum=1)


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ApiError("Email inválido", 400)
    return email


def validate_status(status: str) -> str:
    if status not in VALID_STATUSES:
        raise ApiError("Status inválido", 400)
    return status


def validate_priority(priority) -> int:
    parsed = _as_int(priority, "Prioridade", minimum=MIN_PRIORITY)
    if parsed > MAX_PRIORITY:
        raise ApiError(f"Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}", 400)
    return parsed


def validate_role(role: str) -> str:
    if role not in VALID_ROLES:
        raise ApiError("Role inválido", 400)
    return role


def validate_color(color: str) -> str:
    if not isinstance(color, str) or not COLOR_RE.match(color):
        raise ApiError("Cor inválida. Use o formato #RRGGBB", 400)
    return color


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ApiError("Formato de data inválido. Use YYYY-MM-DD", 400)


def _normalize_tags(value):
    if value is None:
        return None
    if isinstance(value, list):
        if not all(isinstance(tag, str) for tag in value):
            raise ApiError("Tags inválidas", 400)
        return ",".join(tag.strip() for tag in value if tag.strip())
    if isinstance(value, str):
        return value.strip()
    raise ApiError("Tags inválidas", 400)


def validate_task_payload(payload, partial: bool = False) -> dict:
    data = _require_dict(payload)
    result = {}

    if not partial or "title" in data:
        title = data.get("title")
        if not isinstance(title, str):
            raise ApiError("Título é obrigatório", 400)
        title = title.strip()
        if len(title) < MIN_TITLE_LENGTH:
            raise ApiError("Título muito curto", 400)
        if len(title) > MAX_TITLE_LENGTH:
            raise ApiError("Título muito longo", 400)
        result["title"] = title

    if "description" in data:
        description = data.get("description")
        if description is None:
            description = ""
        if not isinstance(description, str):
            raise ApiError("Descrição inválida", 400)
        result["description"] = description
    elif not partial:
        result["description"] = ""

    if "status" in data:
        result["status"] = validate_status(data.get("status"))
    elif not partial:
        result["status"] = "pending"

    if "priority" in data:
        result["priority"] = validate_priority(data.get("priority"))
    elif not partial:
        result["priority"] = DEFAULT_PRIORITY

    if "user_id" in data:
        result["user_id"] = _optional_id(data.get("user_id"), "Usuário")
    elif not partial:
        result["user_id"] = None

    if "category_id" in data:
        result["category_id"] = _optional_id(data.get("category_id"), "Categoria")
    elif not partial:
        result["category_id"] = None

    if "due_date" in data:
        due_date = data.get("due_date")
        result["due_date"] = None if due_date in (None, "") else parse_date(due_date)
    elif not partial:
        result["due_date"] = None

    if "tags" in data:
        result["tags"] = _normalize_tags(data.get("tags"))
    elif not partial:
        result["tags"] = None

    return result


def validate_user_payload(payload, partial: bool = False) -> dict:
    data = _require_dict(payload)
    result = {}

    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ApiError("Nome é obrigatório", 400)
        result["name"] = name.strip()

    if not partial or "email" in data:
        email = data.get("email")
        if not isinstance(email, str) or not email.strip():
            raise ApiError("Email é obrigatório", 400)
        result["email"] = validate_email(email)

    if not partial or "password" in data:
        password = data.get("password")
        if not isinstance(password, str):
            raise ApiError("Senha é obrigatória", 400)
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ApiError(
                f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres",
                400,
            )
        result["password"] = password

    if "role" in data:
        result["role"] = validate_role(data.get("role"))
    elif not partial:
        result["role"] = "user"

    if "active" in data:
        if not isinstance(data.get("active"), bool):
            raise ApiError("Active deve ser booleano", 400)
        result["active"] = data.get("active")

    return result


def validate_login_payload(payload) -> dict:
    data = _require_dict(payload)
    email = data.get("email")
    password = data.get("password")
    if not isinstance(email, str) or not isinstance(password, str):
        raise ApiError("Email e senha são obrigatórios", 400)
    if not email.strip() or not password:
        raise ApiError("Email e senha são obrigatórios", 400)
    return {"email": validate_email(email), "password": password}


def validate_category_payload(payload, partial: bool = False) -> dict:
    data = _require_dict(payload)
    result = {}

    if not partial or "name" in data:
        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ApiError("Nome é obrigatório", 400)
        result["name"] = name.strip()

    if "description" in data:
        description = data.get("description") or ""
        if not isinstance(description, str):
            raise ApiError("Descrição inválida", 400)
        result["description"] = description
    elif not partial:
        result["description"] = ""

    if "color" in data:
        result["color"] = validate_color(data.get("color"))
    elif not partial:
        result["color"] = DEFAULT_COLOR

    return result


def parse_pagination(args) -> tuple[int, int]:
    page = _as_int(args.get("page", 1), "page", minimum=1)
    per_page = _as_int(
        args.get("per_page", DEFAULT_PAGE_SIZE),
        "per_page",
        minimum=1,
    )
    return page, min(per_page, MAX_PAGE_SIZE)


def validate_search_filters(args) -> dict:
    query = (args.get("q") or "").strip() or None
    status = args.get("status") or None
    if status:
        validate_status(status)

    priority = args.get("priority") or None
    if priority:
        priority = validate_priority(priority)

    user_id = args.get("user_id") or None
    if user_id:
        user_id = _as_int(user_id, "Usuário", minimum=1)

    return {
        "query": query,
        "status": status,
        "priority": priority,
        "user_id": user_id,
    }
