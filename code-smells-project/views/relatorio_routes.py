from flask import Blueprint

from controllers import relatorio_controller

relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.get("/relatorios/vendas")
def relatorio_vendas():
    return relatorio_controller.vendas()
