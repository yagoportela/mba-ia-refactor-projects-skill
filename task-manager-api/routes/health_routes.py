from flask import Blueprint, jsonify

from utils.datetime_utils import utcnow_iso

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok", "timestamp": utcnow_iso()})


@health_bp.get("/")
def index():
    return jsonify({"message": "Task Manager API", "version": "1.0"})
