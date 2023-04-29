from flask import Blueprint

bp = Blueprint('dashboard', __name__, url_prefix='/admin')

from bet.dashboard import routes
