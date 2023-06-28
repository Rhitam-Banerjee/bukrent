import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(script_info=None):
    app = Flask(__name__)
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, supports_credentials=True, origins=[
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:3006',
        "https://bukrent.com",
        "https://www.bukrent.com",
        "https://payment.bukrent.com",
        "https://admin.bukrent.com",
        "https://delivery.bukrent.com",
        "https://edit.bukrent.com",
        "https://ops.bukrent.com",

        "https://brightr.vercel.app",
        "https://brightr.com",
        "https://brightr.club",
        "https://edit.brightr.club",
        "https://test.brightr.club",
        "https://admin.brightr.club",
        "https://delivery.brightr.club",
        "https://editold.brightr.club",
        "https://ops.brightr.club",
    ])

    from app.api.api import api
    app.register_blueprint(api)

    from app.api_v2 import api_v2
    app.register_blueprint(api_v2)

    from app.api_v2 import api_v2_books
    app.register_blueprint(api_v2_books)

    from app.api_admin import api_admin
    app.register_blueprint(api_admin)

    from app.api_delivery.api_delivery import api_delivery
    app.register_blueprint(api_delivery)

    from app.views.views import views
    app.register_blueprint(views)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}
    return app
