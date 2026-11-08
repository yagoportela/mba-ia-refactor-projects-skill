from flask import Blueprint

from controllers import health_controller

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    return health_controller.health()
