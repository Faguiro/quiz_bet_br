from flask import render_template, redirect, url_for, flash, request,abort
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from bet import db, Config
#rom bet.pay import bp

from . import bp

from bet.models import User, Pagamento

import stripe

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

@bp.route('/pagamento')
def order():
    print('ok') 
    return render_template('pay/pagamento.html', products=products, endpoint='pagamento')

@bp.route('/pagamento/codigo/<codigo>', methods=['GET', 'POST'])
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
    print('Success')
    return render_template('pay/pagamento/success')

@bp.route('/pagamento/cancel')
def cancel():
    return render_template('pay.cancel.html')

@bp.route('/pagamento/event', methods=['POST'])
def new_event():
    with bp.app_context():  # Criar contexto de aplicação
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