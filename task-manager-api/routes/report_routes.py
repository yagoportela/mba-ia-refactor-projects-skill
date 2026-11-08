from flask import Blueprint

from controllers import report_controller

report_bp = Blueprint("reports", __name__)


@report_bp.get("/reports/summary")
def summary_report():
    return report_controller.summary()


@report_bp.get("/reports/user/<int:user_id>")
def user_report(user_id):
    return report_controller.user_report(user_id)
