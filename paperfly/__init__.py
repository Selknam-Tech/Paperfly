from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from paperfly.utils.key_generator import create_config_with_keys
import logging
import os


db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config')

    app.config['BASE_WORKSPACE'] = os.path.join(app.root_path, app.config['WORKSPACE']); 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.config['BASE_WORKSPACE'], 'app.sqlite')

    os.makedirs(os.path.join(app.config['BASE_WORKSPACE']),exist_ok=True)

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers

    db.init_app(app)
    migrate.init_app(app, db)

    app.app_context().push()

    with app.app_context():
        from paperfly.models import db as db_models
        app.logger.info('Crea la base de datos')
        db_models.create_all()

    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)
    with open(os.path.join(app.root_path,'version.txt'), 'r') as file:
        run_number = file.read().strip()
        app.logger.info('Paperfly Start - v0.1.4 | ' + run_number)

    create_config_with_keys(logger=app.logger, root_path=app.root_path)

    # Registra el blueprint
    from paperfly.main import bp as main_execution_bp
    app.register_blueprint(main_execution_bp, url_prefix='/')

    # Registra el blueprint
    from paperfly.notebook_execution import bp as notebook_execution_bp
    app.register_blueprint(notebook_execution_bp, url_prefix='/notebook')

    # Registra el blueprint de repositorio
    from paperfly.repo import bp as repo_bp
    app.register_blueprint(repo_bp, url_prefix='/repo')

    return app