from flask import Blueprint

bp = Blueprint('auth', __name__)

from bet.auth import routes
