from flask import Blueprint

from controllers import admin_controller
from middlewares.auth import require_admin_token

admin_bp = Blueprint("admin", __name__)


@admin_bp.post("/admin/reset-db")
@require_admin_token
def reset_database():
    return admin_controller.reset_database()


@admin_bp.post("/admin/query")
def executar_query():
    return admin_controller.execute_query()
