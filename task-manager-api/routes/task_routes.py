from flask import Blueprint, request

from controllers import task_controller

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/tasks")
def get_tasks():
    return task_controller.list_tasks(request.args)


@tasks_bp.get("/tasks/search")
def search_tasks():
    return task_controller.search_tasks(request.args)


@tasks_bp.get("/tasks/stats")
def task_stats():
    return task_controller.task_stats()


@tasks_bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    return task_controller.get_task(task_id)


@tasks_bp.post("/tasks")
def create_task():
    return task_controller.create_task(request.get_json(silent=True))


@tasks_bp.put("/tasks/<int:task_id>")
def update_task(task_id):
    return task_controller.update_task(task_id, request.get_json(silent=True))


@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    return task_controller.delete_task(task_id)
