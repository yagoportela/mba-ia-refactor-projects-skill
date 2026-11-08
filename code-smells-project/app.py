import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Settings
from database import init_app, init_db
from middlewares.error_handler import register_error_handlers
from views import register_blueprints


def create_app(settings=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(settings or Settings)

    origins = app.config.get("CORS_ORIGINS") or []
    if origins:
        CORS(app, origins=origins)

    init_app(app)
    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if app.config["DEBUG"] else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
