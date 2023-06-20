from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, Response, abort
from flask_login import login_user
from flask_login import current_user, login_required
from langdetect import detect, LangDetectException
from bet import db
from bet.quizzes.forms import  create_quiz_form
from bet.models import User, Post, Quiz, Pagamento, Produto,Jogo, Rodada
from bet.translate import translate
from bet.quizzes import bp
import io
from io import BytesIO
from PIL import Image
from bet import db, Config
import os
import re
from unidecode import unidecode
import pandas as pd 
from itertools import zip_longest

import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

def zip_lists(list1, list2):
    return zip_longest(list1, list2)

def convert_answer(answer):
    if answer == 1:
        return 'mandante'
    elif answer == 2:
        return 'empate'
    elif answer == 3:
        return 'visitante'
    else:
        return None



def get_selecao_dict(rodada):
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(current_dir, 'static', 'data', 'csv', 'dados_rodada.csv')
    df = pd.read_csv(csv_path)
    selecao = df.loc[df['rodada'] == str(rodada) + 'ª', ['mandante', 'visitante']]
    selecao_dict = selecao.to_dict(orient='records')
    return selecao_dict



def format_team_name(team_name):
        # Remove acentos e caracteres especiais
        team_name = unidecode(team_name)
        #team_name = re.sub('[^0-9a-zA-Z]+', '', team_name)
        # Converte para caixa baixa e substitui espaços por underline
        team_name = team_name.lower().replace(' ', '_')
        return team_name





@bp.route('/quiz/<int:rodada>', methods=['GET', 'POST'])
@login_required
def quiz_rodada(rodada):
    rodada_obj = Jogo.query.filter_by(rodada_id=rodada).first()
    if not rodada_obj:
        flash('Rodada não encontrada.', 'danger')
        return redirect(url_for('quizzes.index'))
    
    selecao = db.session.query(Jogo.mandante, Jogo.visitante).filter_by(rodada_id=rodada).all()
    selecao_dict =  [{'time1': mandante, 'time2': visitante} for mandante, visitante in selecao]
    
    form = create_quiz_form(selecao_dict)
    times = selecao_dict
    print (type(selecao_dict))
    
    if request.method == 'POST':
        if form.validate_on_submit():
            answer0 = convert_answer(form.answer0.data)
            answer1 = convert_answer(form.answer1.data)
            answer2 = convert_answer(form.answer2.data)
            answer3 = convert_answer(form.answer3.data)
            answer4 = convert_answer(form.answer4.data)
            answer5 = convert_answer(form.answer5.data)
            answer6 = convert_answer(form.answer6.data)
            answer7 = convert_answer(form.answer7.data)
            answer8 = convert_answer(form.answer8.data)
            answer9 = convert_answer(form.answer9.data)
            answered = True
            
            # Crie um objeto Quiz com os valores dos campos do formulário
            quiz = Quiz(
                rodada_id=rodada_obj.id,
                answer0=answer0,
                answer1=answer1,
                answer2=answer2,
                answer3=answer3,
                answer4=answer4,
                answer5=answer5,
                answer6=answer6,
                answer7=answer7,
                answer8=answer8,
                answer9=answer9,
                answered=answered,
                user_id=current_user.id
            )
            
            db.session.add(quiz)
            db.session.commit()
            
            return redirect(url_for('quizzes.result', 
                                    answer1=answer1, 
                                    answer2=answer2, 
                                    answer3=answer3, 
                                    answer4=answer4, 
                                    answer5=answer5, 
                                    answer6=answer6))
    
    return render_template('rodadas.html', form=form, times=times, rodada=rodada, format_team_name=format_team_name)

   

@bp.route('/result/')
@login_required
def result():
    return "Results"

@bp.route('/result/<int:rodada>')
@login_required
def result_rodada(rodada):
    answers = []
    tabela = []
    # Verificar se o usuário já respondeu o quiz
    quiz_respondido = Quiz.query.filter_by(user_id=current_user.id, answered=True)
    if quiz_respondido:
        for item in quiz_respondido:
            answers.append(item)
            tabela.append(get_selecao_dict(item.rodada))
        return render_template('result.html', answers=answers, tabela=tabela, rodada=rodada)


@bp.route('/migrate/id')   
def migrate_data():
    # Caminho do arquivo CSV    
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(current_dir, 'static', 'data', 'csv', 'dados_rodada.csv')
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extrair os dados do CSV
            rodada_str = row['rodada']
            rodada_str = rodada_str.replace('ª', '')  # Remove o caractere "ª"
            rodada = int(rodada_str)
            mandante = row['mandante']
            placar_mandante = row['placar_mandante']
            placar_visitante = row['placar_visitante']
            visitante = row['visitante']
            data_inicio = datetime.strptime(row['data_inicio'], '%Y-%m-%d').date()
            data_fim = datetime.strptime(row['data_fim'], '%Y-%m-%d').date()
      
            # Criar uma nova instância de Rodada se a rodada ainda não existir
            rodada_obj = Rodada.query.filter_by(rodada=rodada).first()
            if not rodada_obj:
                rodada_obj = Rodada(rodada=rodada, data_inicio=data_inicio, data_fim=data_fim)
                db.session.add(rodada_obj)
                db.session.commit()

            # Criar uma nova instância de Jogo
            jogo = Jogo(rodada_id=rodada_obj.id, mandante=mandante, placar_mandante=placar_mandante,
                        placar_visitante=placar_visitante, visitante=visitante)

            # Adicionar o jogo à sessão do SQLAlchemy
            db.session.add(jogo)

    # Realizar o commit das alterações no banco de dados
    db.session.commit()

    return "Migração concluida"
