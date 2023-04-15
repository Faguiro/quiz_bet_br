from flask import Blueprint

bp = Blueprint('pay', __name__)

from bet.pay import routes
