from flask import jsonify
from sqlalchemy import func, update

from database import db
from utils.errors import ApiError
from models.category import Category
from models.task import Task
from utils.validators import parse_pagination, validate_category_payload


def list_categories(args):
    page, per_page = parse_pagination(args)
    total = db.session.scalar(db.select(func.count(Category.id))) or 0

    rows = db.session.execute(
        db.select(Category, func.count(Task.id).label("task_count"))
        .outerjoin(Task, Task.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.id)
        .limit(per_page)
        .offset((page - 1) * per_page)
    ).all()

    items = []
    for category, task_count in rows:
        data = category.to_dict()
        data["task_count"] = task_count
        items.append(data)

    return jsonify(items), 200, {"X-Total-Count": str(total)}


def create_category(payload):
    data = validate_category_payload(payload)
    category = Category(**data)

    try:
        db.session.add(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(category.to_dict()), 201


def update_category(category_id: int, payload):
    category = db.session.get(Category, category_id)
    if category is None:
        raise ApiError("Categoria não encontrada", 404)

    data = validate_category_payload(payload, partial=True)
    for field, value in data.items():
        setattr(category, field, value)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(category.to_dict()), 200


def delete_category(category_id: int):
    category = db.session.get(Category, category_id)
    if category is None:
        raise ApiError("Categoria não encontrada", 404)

    try:
        db.session.execute(
            update(Task)
            .where(Task.category_id == category_id)
            .values(category_id=None)
        )
        db.session.delete(category)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Categoria deletada"}), 200
