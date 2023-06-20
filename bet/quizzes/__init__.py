from flask import Blueprint


bp = Blueprint('quizzes', __name__)


from . import routes
