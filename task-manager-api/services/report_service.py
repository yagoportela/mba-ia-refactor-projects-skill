from datetime import timedelta

from sqlalchemy import case, func

from database import db
from utils.errors import ApiError
from models.category import Category
from models.task import Task
from models.user import User
from utils.constants import PRIORITY_LABELS, VALID_STATUSES
from utils.datetime_utils import utcnow, utcnow_iso


def _scalar_count(statement) -> int:
    return db.session.scalar(statement) or 0


def summary() -> dict:
    total_tasks = _scalar_count(db.select(func.count(Task.id)))
    total_users = _scalar_count(db.select(func.count(User.id)))
    total_categories = _scalar_count(db.select(func.count(Category.id)))

    status_rows = db.session.execute(
        db.select(Task.status, func.count(Task.id)).group_by(Task.status)
    ).all()
    status_counts = {status: 0 for status in VALID_STATUSES}
    for status, count in status_rows:
        if status in status_counts:
            status_counts[status] = count

    priority_rows = db.session.execute(
        db.select(Task.priority, func.count(Task.id)).group_by(Task.priority)
    ).all()
    priority_counts = {priority: 0 for priority in PRIORITY_LABELS}
    for priority, count in priority_rows:
        if priority in priority_counts:
            priority_counts[priority] = count

    now = utcnow()
    overdue_tasks = db.session.execute(
        db.select(Task)
        .where(
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status.notin_(("done", "cancelled")),
        )
        .order_by(Task.due_date)
    ).scalars().all()

    overdue_list = [
        {
            "id": task.id,
            "title": task.title,
            "due_date": str(task.due_date),
            "days_overdue": (now - task.due_date).days,
        }
        for task in overdue_tasks
    ]

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = _scalar_count(
        db.select(func.count(Task.id)).where(Task.created_at >= seven_days_ago)
    )
    recent_done = _scalar_count(
        db.select(func.count(Task.id)).where(
            Task.status == "done",
            Task.updated_at >= seven_days_ago,
        )
    )

    user_rows = db.session.execute(
        db.select(
            User.id,
            User.name,
            func.count(Task.id).label("total_tasks"),
            func.coalesce(
                func.sum(case((Task.status == "done", 1), else_=0)),
                0,
            ).label("completed_tasks"),
        )
        .outerjoin(Task, Task.user_id == User.id)
        .group_by(User.id, User.name)
        .order_by(User.id)
    ).all()

    user_stats = []
    for user_id, user_name, user_total, user_completed in user_rows:
        user_stats.append({
            "user_id": user_id,
            "user_name": user_name,
            "total_tasks": user_total,
            "completed_tasks": user_completed,
            "completion_rate": (
                round((user_completed / user_total) * 100, 2)
                if user_total > 0
                else 0
            ),
        })

    return {
        "generated_at": utcnow_iso(),
        "overview": {
            "total_tasks": total_tasks,
            "total_users": total_users,
            "total_categories": total_categories,
        },
        "tasks_by_status": status_counts,
        "tasks_by_priority": {
            PRIORITY_LABELS[priority]: count
            for priority, count in priority_counts.items()
        },
        "overdue": {
            "count": len(overdue_list),
            "tasks": overdue_list,
        },
        "recent_activity": {
            "tasks_created_last_7_days": recent_tasks,
            "tasks_completed_last_7_days": recent_done,
        },
        "user_productivity": user_stats,
    }


def user_report(user_id: int) -> dict:
    user = db.session.get(User, user_id)
    if user is None:
        raise ApiError("Usuário não encontrado", 404)

    tasks = db.session.execute(
        db.select(Task).where(Task.user_id == user_id).order_by(Task.id)
    ).scalars().all()

    counts = {status: 0 for status in VALID_STATUSES}
    overdue = 0
    high_priority = 0

    for task in tasks:
        if task.status in counts:
            counts[task.status] += 1
        if task.priority <= 2:
            high_priority += 1
        if task.is_overdue():
            overdue += 1

    total = len(tasks)
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
        "statistics": {
            "total_tasks": total,
            "done": counts["done"],
            "pending": counts["pending"],
            "in_progress": counts["in_progress"],
            "cancelled": counts["cancelled"],
            "overdue": overdue,
            "high_priority": high_priority,
            "completion_rate": (
                round((counts["done"] / total) * 100, 2) if total > 0 else 0
            ),
        },
    }
