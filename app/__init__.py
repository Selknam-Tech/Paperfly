from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.utils.key_generator import create_config_with_keys
import logging

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)
    app.logger.info('Paperfly Start v0.1.2')
    app.app_context().push()

    create_config_with_keys(logger=app.logger, root_path=app.root_path)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registra el blueprint
    from app.main import bp as main_execution_bp
    app.register_blueprint(main_execution_bp, url_prefix='/')

    # Registra el blueprint
    from app.notebook_execution import bp as notebook_execution_bp
    app.register_blueprint(notebook_execution_bp, url_prefix='/notebook')

    # Registra el blueprint de repositorio
    from app.repo import bp as repo_bp
    app.register_blueprint(repo_bp, url_prefix='/repo')

    return app