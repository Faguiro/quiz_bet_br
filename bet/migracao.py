import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from bet import app, db
from bet.models import Jogo, Rodada
import os

def migrate_data():
    # Caminho do arquivo CSV
    
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(current_dir, 'static', 'data', 'csv', 'dados_rodada.csv')

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Extrair os dados do CSV
            rodada = int(row['rodada'])
            time1 = row['time1']
            placar_time1 = row['placar_time1']
            placar_time2 = row['placar_time2']
            time2 = row['time2']
            data_inicio = datetime.strptime(row['data_inicio'], '%Y-%m-%d').date()
            data_fim = datetime.strptime(row['data_fim'], '%Y-%m-%d').date()

            # Criar uma nova instância de Rodada se a rodada ainda não existir
            rodada_obj = Rodada.query.filter_by(rodada=rodada).first()
            if not rodada_obj:
                rodada_obj = Rodada(rodada=rodada, data_inicio=data_inicio, data_fim=data_fim)
                db.session.add(rodada_obj)
                db.session.commit()

            # Criar uma nova instância de Jogo
            jogo = Jogo(rodada_id=rodada_obj.id, time1=time1, placar_time1=placar_time1,
                        placar_time2=placar_time2, time2=time2)

            # Adicionar o jogo à sessão do SQLAlchemy
            db.session.add(jogo)

    # Realizar o commit das alterações no banco de dados
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        migrate_data()
        print('Migração concluída com sucesso.')
