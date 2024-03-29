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

    CORS(app, supports_credentials=True, resources=r'/api/*', origins=['http://localhost:3000', 'https://bukrent-browse-library.vercel.app', 'https://bukrent.vercel.app', 'https://www.bukrent.com', 'https://main.bukrent.com', 'https://payment.bukrent.com'])

    from app.api.api import api
    app.register_blueprint(api)

    from app.api_v2.api_v2 import api_v2
    app.register_blueprint(api_v2)

    from app.views.views import views
    app.register_blueprint(views)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}
    return app
