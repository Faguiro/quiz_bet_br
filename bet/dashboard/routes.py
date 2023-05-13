from flask import render_template, redirect, url_for, flash, request, abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import _
from bet import db
from bet.dashboard import bp
from bet.models import User
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView




@bp.route('/prismas', methods=['GET', 'POST'])

def prismas():
    # theme = User.query.filter_by(teheme= current_user.theme).first_or_404()
    theme = request.args.get('theme', 'sketchy')
    return render_template('prisma.html', theme=theme)


