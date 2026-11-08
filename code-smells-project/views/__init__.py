from views.admin_routes import admin_bp
from views.health_routes import health_bp
from views.index_routes import index_bp
from views.pedido_routes import pedidos_bp
from views.produto_routes import produtos_bp
from views.relatorio_routes import relatorios_bp
from views.usuario_routes import usuarios_bp

BLUEPRINTS = (
    index_bp,
    produtos_bp,
    usuarios_bp,
    pedidos_bp,
    relatorios_bp,
    health_bp,
    admin_bp,
)


def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
