from flask import Blueprint

bp = Blueprint('dashboard', __name__)

from bet.dashboard import routes
