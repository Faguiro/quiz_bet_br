from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, Response, abort
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from bet import db
from bet.main.forms import EditProfileForm, EmptyForm, PostForm, QuizForm
from bet.models import User, Post, Quiz, Pagamento
from bet.translate import translate
from bet.main import bp
import io
from io import BytesIO
from PIL import Image
import  stripe
from bet import db, Config




@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Home'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url) 


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
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        # Convert the image to PNG format
        img_data = form.profile_photo.data
        if img_data:
            img_data = img_data.read()
            img = Image.open(io.BytesIO(img_data))
            img = img.convert('RGBA')

            # Redimensionar a imagem para que o tamanho do arquivo não ultrapasse 150KB
            max_size = (150, 150)
            img.thumbnail(max_size)

            img_file = io.BytesIO()
            img.save(img_file, format='PNG')
            img_data = img_file.getvalue()

        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.profile_photo = img_data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form, username=User.username)


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
    quiz_respondido = Quiz.query.filter_by(user_id=current_user.id, answered=True).first()

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
def result():
    form = QuizForm()
    try:
        answers = Quiz.query.filter_by(user_id=current_user.id).first()
        answer1 = answers.answer1
        answer2 = answers.answer2
        answer3 = answers.answer3
        answer4 = answers.answer4
        answer5 = answers.answer5
        answer6 = answers.answer6
        answer7 = answers.answer7
        answer8 = answers.answer8
        answer9 = answers.answer9
        answer10 = answers.answer10
        return render_template('result.html', answer1=answer1, answer2=answer2, answer3=answer3, answer4=answer4, answer5=answer5, answer6=answer6,answer7=answer7,answer8=answer8,answer9=answer9,answer10=answer10)
    except:
        return redirect(url_for('main.index'))

@bp.route('/user/<username>/image')
def show_post_image(username):
    user = User.query.filter_by(username=username).first()
    if user and user.profile_photo: # Verifica se o usuário existe e possui uma foto de perfil
        return Response(user.profile_photo, content_type='image/png')
    return 'Image not found', 404




####################### PAGAMENTOS #################

stripe.api_key = Config.STRIPE_SECRET_KEY

products = {
    'Suporte total': {
        'codigo': 'full',
        'name': 'Todas as rodadas do Brasileirão',
        'price': 5000,
    },
    'Suporte por rodada': {
        'codigo': 'unidade',
        'name': 'Rodadas  avulsas do Brasileirão',
        'price': 500,
        'por': 'rodada',
        'adjustable_quantity': {
            'enabled': True,
            'minimum': 1,
            'maximum': 15,
        },
    },
}



@bp.route('/pagamentos')
def pagamentos():
    return render_template('pagamentos.html', products=products)


@bp.route('/pagamento/<codigo>', methods=['POST'])
def order_codigo(codigo):

    codigo_escolhido = codigo
    produto_encontrado = None
    for produto in products.values():
        if 'codigo' in produto and produto['codigo'] == codigo_escolhido:
            produto_encontrado = produto
            break
    
    # Verificar se o produto foi encontrado e imprimir seu nome
    if not produto_encontrado:
        print('abortado', codigo)
        abort(404)
    else:  
        product =  produto_encontrado
        print(product)

        line_item = {
            'price_data': {
                'product_data': {
                    'name': product['name'],
                },
                'unit_amount': product['price'],
                'currency': 'BRL',
            },
            'quantity': 1,
            'adjustable_quantity': product.get('adjustable_quantity', {'enabled': False}),
        }
        print (line_item)


        checkout_session = stripe.checkout.Session.create(
            line_items=[line_item],
            payment_method_types=['card'],
            mode='payment',
            success_url=request.host_url + 'pagamento/success',
            cancel_url=request.host_url + 'pagamento/cancel',
        )
        return redirect(checkout_session.url)

@bp.route('/pagamento/success')
def success():
    return render_template('success.html')

@bp.route('/pagamento/cancel')
def cancel():
    return render_template('cancel.html')

@bp.route('/event', methods=['POST'])
def new_event():
    
    event = None
    payload = request.data
    signature = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload, signature, Config.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print(e)
        abort(400)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object'].id, expand=['line_items'])
        #print(f'Sale to {session.customer_details.email}:')
        for item in session.line_items.data:
            #print (item)
            print (session.customer_details)
            # Criar instância do modelo Produto e salvar no banco de dados
            produto = Pagamento(pagador = session.customer_details.name ,nome=item.description, valor=item.amount_total/100, email=session.customer_details.email)
            db.session.add(produto)
            db.session.commit()
            """ print(f'  - {item.quantity} {item.description} '
                    f'${item.amount_total/100:.02f} {item.currency.upper()}') """

    return {'success': True}

