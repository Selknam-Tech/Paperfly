from flask import Blueprint

bp = Blueprint('repo', __name__)

from app.repo import routes