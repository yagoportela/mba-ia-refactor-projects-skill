from routes.category_routes import categories_bp
from routes.health_routes import health_bp
from routes.report_routes import report_bp
from routes.task_routes import tasks_bp
from routes.user_routes import user_bp

BLUEPRINTS = (
    health_bp,
    tasks_bp,
    user_bp,
    categories_bp,
    report_bp,
)


def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
