from flask import Blueprint

bp = Blueprint('notebook_execution', __name__)

from app.notebook_execution import routes
