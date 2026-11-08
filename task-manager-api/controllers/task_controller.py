from flask import current_app, jsonify
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from database import db
from utils.errors import ApiError
from models.category import Category
from models.task import Task
from models.user import User
from services.notification_service import NotificationService
from utils.constants import VALID_STATUSES
from utils.datetime_utils import utcnow
from utils.validators import (
    parse_pagination,
    validate_search_filters,
    validate_task_payload,
)


def _count(statement) -> int:
    return db.session.scalar(statement) or 0


def list_tasks(args):
    page, per_page = parse_pagination(args)
    query = (
        db.select(Task)
        .options(joinedload(Task.user), joinedload(Task.category))
        .order_by(Task.id)
    )
    pagination = db.paginate(
        query,
        page=page,
        per_page=per_page,
        error_out=False,
    )
    items = [
        task.to_dict(include_user=True, include_category=True)
        for task in pagination.items
    ]
    return jsonify(items), 200, {"X-Total-Count": str(pagination.total)}


def get_task(task_id: int):
    task = db.session.get(Task, task_id)
    if task is None:
        raise ApiError("Task não encontrada", 404)
    return jsonify(task.to_dict()), 200


def create_task(payload):
    data = validate_task_payload(payload)

    user = None
    if data.get("user_id"):
        user = db.session.get(User, data["user_id"])
        if user is None:
            raise ApiError("Usuário não encontrado", 404)

    if data.get("category_id"):
        category = db.session.get(Category, data["category_id"])
        if category is None:
            raise ApiError("Categoria não encontrada", 404)

    task = Task(**data)
    try:
        db.session.add(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    if user is not None:
        NotificationService.from_config(current_app.config).notify_task_assigned(user, task)

    return jsonify(task.to_dict()), 201


def update_task(task_id: int, payload):
    task = db.session.get(Task, task_id)
    if task is None:
        raise ApiError("Task não encontrada", 404)

    data = validate_task_payload(payload, partial=True)

    if data.get("user_id"):
        if db.session.get(User, data["user_id"]) is None:
            raise ApiError("Usuário não encontrado", 404)

    if data.get("category_id"):
        if db.session.get(Category, data["category_id"]) is None:
            raise ApiError("Categoria não encontrada", 404)

    for field, value in data.items():
        setattr(task, field, value)
    task.updated_at = utcnow()

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(task.to_dict()), 200


def delete_task(task_id: int):
    task = db.session.get(Task, task_id)
    if task is None:
        raise ApiError("Task não encontrada", 404)

    try:
        db.session.delete(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks(args):
    filters = validate_search_filters(args)
    page, per_page = parse_pagination(args)

    conditions = []
    if filters["query"]:
        pattern = f"%{filters['query']}%"
        conditions.append(or_(Task.title.like(pattern), Task.description.like(pattern)))
    if filters["status"]:
        conditions.append(Task.status == filters["status"])
    if filters["priority"]:
        conditions.append(Task.priority == filters["priority"])
    if filters["user_id"]:
        conditions.append(Task.user_id == filters["user_id"])

    query = db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
    if conditions:
        query = query.where(*conditions)
    query = query.order_by(Task.id)

    pagination = db.paginate(
        query,
        page=page,
        per_page=per_page,
        error_out=False,
    )
    return (
        jsonify([task.to_dict() for task in pagination.items]),
        200,
        {"X-Total-Count": str(pagination.total)},
    )


def task_stats():
    total = _count(db.select(func.count(Task.id)))

    status_rows = db.session.execute(
        db.select(Task.status, func.count(Task.id)).group_by(Task.status)
    ).all()
    status_counts = {status: 0 for status in VALID_STATUSES}
    for status, count in status_rows:
        if status in status_counts:
            status_counts[status] = count

    overdue = _count(
        db.select(func.count(Task.id)).where(
            Task.due_date.isnot(None),
            Task.due_date < utcnow(),
            Task.status.notin_(("done", "cancelled")),
        )
    )

    return jsonify({
        "total": total,
        "pending": status_counts["pending"],
        "in_progress": status_counts["in_progress"],
        "done": status_counts["done"],
        "cancelled": status_counts["cancelled"],
        "overdue": overdue,
        "completion_rate": round((status_counts["done"] / total) * 100, 2) if total > 0 else 0,
    }), 200
