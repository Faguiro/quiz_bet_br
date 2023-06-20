from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, Response, abort
from flask_login import login_user
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException
from bet import db
from bet.main.forms import EditProfileForm, EmptyForm, PostForm
from bet.models import User, Post, Quiz, Pagamento, Produto
from bet.translate import translate
from bet.pay import bp
import io
from io import BytesIO
from PIL import Image
import stripe
import mercadopago
from bet import db, Config
import os
from jinja2 import Template, UndefinedError


sdk = mercadopago.SDK(os.getenv('MP_ACCESS_TOKEN'))








####################### PAGAMENTOS #################
@bp.route('/comprarcreditos')
def comprar_creditos():
    # Dados dos métodos de pagamento
    metodos_pagamento = [
        #  {'nome': 'Pix', 'imagem': 'pix.png'},
        #  {'nome': 'Mercado Pago', 'imagem': 'mercadopago.png'},
        #  {'nome': 'PicPay', 'imagem': 'picpay.png'},
        {'nome': 'Stripe', 'imagem': 'stripe.png'},
        #  {'nome': 'PayPal', 'imagem': 'paypal.png'}
    ]
    # Renderizando o template com os dados
    return render_template('comprar_creditos.html', metodos_pagamento=metodos_pagamento)


####################### PAGAMENTOS  stripe configurações #################
stripe.api_key = Config.STRIPE_SECRET_KEY


####################### PAGAMENTOS  stripe #################

@bp.route('/pagamento/stripe')
@login_required
def pagamento_stripe():
    # Buscar os produtos do banco de dados
    produtos = Produto.query.all()
    # Passar os produtos para o template renderizar
    return render_template('stripe_pagamentos.html', produtos=produtos)


@bp.route('/stripe_pagamento/<codigo>', methods=['POST'])
@login_required
def stripe_order_codigo(codigo):
    produto_encontrado = Produto.query.filter_by(codigo=codigo).first()
    # Verificar se o produto foi encontrado e imprimir seu nome
    if not produto_encontrado:
        print('Produto não encontrado para o código:', codigo)
        abort(404)
    else:
        product = {
            'name': produto_encontrado.nome,
            # Converter para float,
            'price': int(float(produto_encontrado.preco)*100),
            'adjustable_quantity': {
                'enabled': produto_encontrado.ajustavel_quantidade,
                'minimum': produto_encontrado.quantidade_minima,
                'maximum': produto_encontrado.quantidade_maxima,
            },
        }

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
        print(line_item)

        checkout_session = stripe.checkout.Session.create(
            line_items=[line_item],
            payment_method_types=['card'],
            mode='payment',
            success_url=request.host_url + 'pagamento/stripe/stripe_success',
            cancel_url=request.host_url + 'pagamento/stripe/stripe_cancel',
            metadata={
                # Adiciona o ID do usuário como metadata na sessão de checkout
                'user_id': current_user.id
            }
        )
        return redirect(checkout_session.url)


@bp.route('/pagamento/stripe/stripe_success')
def stripe_success():
    return render_template('stripe_success.html')


@bp.route('/pagamento/stripe/stripe_cancel')
def stripe_cancel():
    return render_template('stripe_cancel.html')


@bp.route('/stripe/event', methods=['POST'])
def new_event():
    event = None
    payload = request.data
    signature = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, Config.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print(e)
        abort(400)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object'].id, expand=['line_items'])
        # Obtém o ID do usuário a partir dos metadata da sessão de checkout
        user_id = session.metadata.get('user_id')

        for item in session.line_items.data:
            try:
                produto = Pagamento(
                    pagador=session.customer_details.name,
                    nome=item.description,
                    valor=item.amount_total/100,
                    email=session.customer_details.email,
                    user_id=user_id  # Atribui o ID do usuário logado à coluna user_id
                )

                db.session.add(produto)
                db.session.commit()

                # Atualiza o saldo do usuário após adicionar o pagamento
                user = User.query.filter_by(id=user_id).first()
                user.atualiza_saldo(item.amount_total/100)
                db.session.commit()

            except Exception as e:
                resp = str(e)
                abort(500)
                return redirect(url_for('main.stripe_cancel'))

    return {'success': True, 'resposta': 'ok'}

#####################################################################


@bp.route('/pagamento/mercado_pago/')
def mercado_pago():
    return render_template('mercado_pago.html', public_key=os.getenv('MP_PUBLIC_KEY'))


@bp.route('/process_payment', methods=['POST'])
def MP_add_income():
    request_values = request.get_json()

    payment_data = {
        "transaction_amount": float(request_values["transaction_amount"]),
        "token": request_values["token"],
        "installments": int(request_values["installments"]),
        "payment_method_id": request_values["payment_method_id"],
        "issuer_id": request_values["issuer_id"],
        "payer": {
            "email": request_values["payer"]["email"],
            "identification": {
                "type": request_values["payer"]["identification"]["type"],
                "number": request_values["payer"]["identification"]["number"]
            }
        }
    }
    print(payment_data)

    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]

    print("status =>", payment["status"])
    print("status_detail =>", payment["status_detail"])
    print("id=>", payment["id"])

    return jsonify(payment), 200
