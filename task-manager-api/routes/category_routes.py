from flask import Blueprint, request

from controllers import category_controller

categories_bp = Blueprint("categories", __name__)


@categories_bp.get("/categories")
def get_categories():
    return category_controller.list_categories(request.args)


@categories_bp.post("/categories")
def create_category():
    return category_controller.create_category(request.get_json(silent=True))


@categories_bp.put("/categories/<int:category_id>")
def update_category(category_id):
    return category_controller.update_category(
        category_id,
        request.get_json(silent=True),
    )


@categories_bp.delete("/categories/<int:category_id>")
def delete_category(category_id):
    return category_controller.delete_category(category_id)
