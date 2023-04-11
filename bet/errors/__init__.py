from flask import Blueprint

bp = Blueprint('errors', __name__)

from bet.errors import handlers
