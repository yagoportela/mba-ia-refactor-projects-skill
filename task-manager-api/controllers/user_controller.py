from flask import current_app, jsonify
from sqlalchemy import func

from database import db
from utils.errors import ApiError
from models.task import Task
from models.user import User
from services.auth_service import create_token
from utils.validators import (
    parse_pagination,
    validate_id,
    validate_login_payload,
    validate_user_payload,
)


def list_users(args):
    page, per_page = parse_pagination(args)
    total = db.session.scalar(db.select(func.count(User.id))) or 0

    rows = db.session.execute(
        db.select(User, func.count(Task.id).label("task_count"))
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id)
        .order_by(User.id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    ).all()

    items = []
    for user, task_count in rows:
        data = user.to_dict()
        data["task_count"] = task_count
        items.append(data)

    return jsonify(items), 200, {"X-Total-Count": str(total)}


def get_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("Usuário não encontrado", 404)

    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == user_id).order_by(Task.id)
    ).scalars().all()

    data = user.to_dict()
    data["tasks"] = [task.to_dict() for task in tasks]
    return jsonify(data), 200


def create_user(payload):
    data = validate_user_payload(payload)

    existing = db.session.execute(
        db.select(User).where(User.email == data["email"])
    ).scalar_one_or_none()
    if existing is not None:
        raise ApiError("Email já cadastrado", 409)

    user = User(
        name=data["name"],
        email=data["email"],
        role=data.get("role", "user"),
    )
    user.set_password(data["password"])

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(user.to_dict()), 201


def update_user(user_id: int, payload):
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("Usuário não encontrado", 404)

    data = validate_user_payload(payload, partial=True)

    if "email" in data:
        existing = db.session.execute(
            db.select(User).where(User.email == data["email"])
        ).scalar_one_or_none()
        if existing is not None and existing.id != user_id:
            raise ApiError("Email já cadastrado", 409)

    for field in ("name", "email", "role", "active"):
        if field in data:
            setattr(user, field, data[field])

    if "password" in data:
        user.set_password(data["password"])

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(user.to_dict()), 200


def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("Usuário não encontrado", 404)

    try:
        db.session.execute(
            db.delete(Task).where(Task.user_id == user_id)
        )
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id: int):
    validate_id(user_id)
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("Usuário não encontrado", 404)

    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == user_id).order_by(Task.id)
    ).scalars().all()

    return jsonify([task.to_dict() for task in tasks]), 200


def login(payload):
    data = validate_login_payload(payload)

    user = db.session.execute(
        db.select(User).where(User.email == data["email"])
    ).scalar_one_or_none()

    if user is None or not user.check_password(data["password"]):
        raise ApiError("Credenciais inválidas", 401)
    if not user.active:
        raise ApiError("Usuário inativo", 403)

    token = create_token(user.id, current_app.config["SECRET_KEY"])
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
        "token": token,
    }), 200
