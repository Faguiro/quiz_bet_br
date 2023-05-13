from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, Response, abort
from flask_login import login_user
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from bet import db
from bet.main.forms import EditProfileForm, EmptyForm, PostForm, QuizForm
from bet.models import User, Post, Quiz, Pagamento, Produto
from bet.translate import translate
from bet.main import bp
import io
from io import BytesIO
from PIL import Image
import stripe
import mercadopago
from bet import db, Config
import os
from jinja2 import Template, UndefinedError


sdk = mercadopago.SDK(os.getenv('MP_ACCESS_TOKEN'))


def get_theme():
    if current_user.is_authenticated:
        return str(current_user.theme)
    else:
        return "zephyr"


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/prisma', methods=['GET', 'POST'])
@login_required
def prisma():
    # theme = User.query.filter_by(teheme= current_user.theme).first_or_404()
    theme = request.args.get('theme', 'sketchy')
    return render_template('prisma.html', theme=theme)


@bp.route('/home')
def home():
    theme = request.args.get('theme', 'light')
    return render_template('home.html', theme=theme)


@bp.route('/criar_publicacao', methods=['GET', 'POST'])
@login_required
def criar_pub():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''

        # Convert the image to PNG format
        img_data = form.post_photo.data
        if (img_data):
            img_data = img_data.read()
            img = Image.open(io.BytesIO(img_data))
            img = img.convert('RGBA')
            img_file = io.BytesIO()
            img.save(img_file, format='PNG')
            img_data = img_file.getvalue()
        else:
            img_data = None

        video_data = form.video.data
        if (video_data):
            video_data = form.video.data.read()
        else:
            video_data = None

        post = Post(body=form.post.data, author=current_user,
                    language=language, img=memoryview(img_data), video=video_data)
        db.session.add(post)
        db.session.commit()
        flash(_('Sua publicação está ao vivo!'))
        return redirect(url_for('main.index'))

    return render_template('criar_pub.html', title=_('Criar publicação'), form=form)


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)

    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/posts/<int:post_id>/image')
def show_post_image(post_id):
    post = Post.query.get(post_id)
    if post:
        return Response(post.img, content_type='image/png')
    return 'Post not found', 404


@bp.route('/posts/<int:post_id>/video')
def post_video(post_id):
    post = Post.query.get_or_404(post_id)
    video_data = post.video

    response = Response(video_data, content_type='video/mp4')
    response.headers.set(
        'Content-Disposition', 'inline', filename='video.mp4')
    return response


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    if current_user.is_authenticated:
        user = User.query.filter_by(
            username=current_user.username).first_or_404()
    else:
        user = User.query.filter_by(id="1").first_or_404()
        login_user(user, remember=form.remember_me.data)
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()

    saldo = str(user.saldo)  # obtém o saldo do usuário
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form, saldo=saldo, teme=get_theme())


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    form = EditProfileForm(current_user.username)
    theme = get_theme()
    if form.validate_on_submit():
        if user != current_user:
            abort(403)
        img_data = form.profile_photo.data
        if img_data:
            img_data = img_data.read()
            img = Image.open(io.BytesIO(img_data))
            img = img.convert('RGBA')
            max_size = (150, 150)
            img.thumbnail(max_size)
            img_file = io.BytesIO()
            img.save(img_file, format='PNG')
            img_data = img_file.getvalue()
        else:
            img_data = current_user.profile_photo

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.profile_photo = img_data
        current_user.theme = form.theme.data
        try:
            db.session.commit()
            flash(_('Suas alterações foram salvas.'))
            return redirect(url_for('main.user', username=current_user.username, theme=theme))
        except db.exc.SQLAlchemyError:
            db.session.rollback()
            flash(
                _('Não foi possível salvar suas alterações. Tente novamente mais tarde.'))
            return redirect(url_for('main.user', username=current_user.username, theme=theme))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Editar Perfil'), form=form, user=user)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    # Verificar se o usuário já respondeu o quiz
    quiz_respondido = Quiz.query.filter_by(
        user_id=current_user.id, answered=True).first()

    if quiz_respondido:
        # Se o usuário já respondeu, redirecionar para a rota de resultado
        return redirect(url_for('main.result'))

    form = QuizForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            answer1 = form.answer1.data
            answer2 = form.answer2.data
            answer3 = form.answer3.data
            answer4 = form.answer4.data
            answer5 = form.answer5.data
            answer6 = form.answer6.data
            answer7 = form.answer7.data
            answer8 = form.answer8.data
            answer9 = form.answer9.data
            answer10 = form.answer10.data
            answered = True

            # Crie um dicionário com os valores dos campos do formulário
            quiz_data = {
                'answer1': answer1,
                'answer2': answer2,
                'answer3': answer3,
                'answer4': answer4,
                'answer5': answer5,
                'answer6': answer6,
                'answer7': answer7,
                'answer8': answer8,
                'answer9': answer9,
                'answer10': answer10,
                'answered': answered,
                'user_id': current_user.id
            }
            # Crie uma nova instância do modelo Quiz com o dicionário de dados
            answer = Quiz(**quiz_data)
            db.session.add(answer)
            db.session.commit()
            return redirect(url_for('main.result', answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4, answer5=answer5, answer6=answer6))
    return render_template('_quiz.html', title='Quiz', form=form)


@bp.route('/result')
@login_required
def result():
    # Verificar se o usuário já respondeu o quiz
    quiz_respondido = Quiz.query.filter_by(
        user_id=current_user.id, answered=True).first()
    if quiz_respondido:
        # Se o usuário já respondeu, redirecionar para a rota de resultado
        try:
            answers = Quiz.query.filter_by(user_id=current_user.id).first()
            quiz_dict = {
                'resposta1': answers.answer1,
                'resposta2': answers.answer2,
                'resposta3': answers.answer3,
                'resposta4': answers.answer4,
                'resposta5': answers.answer5,
                'resposta6': answers.answer6,
                'resposta7': answers.answer7,
                'resposta8': answers.answer8,
                'resposta9': answers.answer9,
                'resposta10': answers.answer10
            }

            return render_template('result.html', answers=quiz_dict)

        except Exception as e:
            print(str(e))
            return (str(e))

    return render_template('_quiz.html', form=QuizForm())


@bp.route('/user/<username>/image')
def show_user_image(username):
    user = User.query.filter_by(username=username).first()
    if user and user.profile_photo:  # Verifica se o usuário existe e possui uma foto de perfil
        return Response(user.profile_photo, content_type='image/png')
    return 'Image not found', 404


