from flask import Blueprint, request

from controllers import user_controller

user_bp = Blueprint("users", __name__)


@user_bp.get("/users")
def get_users():
    return user_controller.list_users(request.args)


@user_bp.get("/users/<int:user_id>")
def get_user(user_id):
    return user_controller.get_user(user_id)


@user_bp.post("/users")
def create_user():
    return user_controller.create_user(request.get_json(silent=True))


@user_bp.put("/users/<int:user_id>")
def update_user(user_id):
    return user_controller.update_user(user_id, request.get_json(silent=True))


@user_bp.delete("/users/<int:user_id>")
def delete_user(user_id):
    return user_controller.delete_user(user_id)


@user_bp.get("/users/<int:user_id>/tasks")
def get_user_tasks(user_id):
    return user_controller.get_user_tasks(user_id)


@user_bp.post("/login")
def login():
    return user_controller.login(request.get_json(silent=True))
