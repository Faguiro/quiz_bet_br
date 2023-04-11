from flask import Blueprint

bp = Blueprint('main', __name__)

from bet.main import routes
