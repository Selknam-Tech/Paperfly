from flask import Blueprint

bp = Blueprint('repo', __name__)

from paperfly.repo import routes