import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(script_info=None):
    app = Flask(__name__)
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.api.api import api
    app.register_blueprint(api)

    from app.views.views import views
    app.register_blueprint(views)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}
    return app