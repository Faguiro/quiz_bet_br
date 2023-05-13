from flask import request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, ValidationError
from flask_babel import _, lazy_gettext as _l
from bet.models import User
from wtforms import RadioField
from flask_wtf.file import FileField, FileAllowed
import pandas as pd  
import os


class EditProfileForm(FlaskForm):
    username = StringField(_l('Nome de usuário'), validators=[DataRequired()])
    about_me = TextAreaField(_l('Sobre mim'),
                             validators=[Length(min=0, max=140)])
    profile_photo = FileField(_l('Foto de perfil'), validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], _l(
            'Only JPEG and PNG images are allowed.'))
    ])
    theme = SelectField('Theme', choices=[
        ('cerulean', 'Cerulean'),
        ('cosmo', 'Cosmo'),
        ('cyborg', 'Cyborg'),
        ('flatly', 'Flatly'),
        ('journal', 'Journal'),
        ('litera', 'Litera'),
        ('lumen', 'Lumen'),
        ('lux', 'Lux'),
        ('materia', 'Materia'),
        ('minty', 'Minty'),
        ('morph', 'Morph'),
        ('pulse', 'Pulse'),
        ('quartz', 'Quartz'),
        ('sandstone', 'Sandstone'),
        ('simplex', 'Simplex'),
        ('sketchy', 'Sketchy'),
        ('slate', 'Slate'),
        ('solar', 'Solar'),
        ('spacelab', 'Spacelab'),
        ('superhero', 'Superhero'),
        ('united', 'United'),
        ('vapor', 'Vapor'),
        ('yeti', 'Yeti'),
        ('zephyr', 'Zephyr')
    ], default='darkly')

    submit = SubmitField(_l('Salvar'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Use um nome diferente.'))


class ThemeForm(FlaskForm):
    theme = SelectField('Theme', choices=[
        ('cerulean', 'Cerulean'),
        ('cosmo', 'Cosmo'),
        ('cyborg', 'Cyborg'),
        ('flatly', 'Flatly'),
        ('journal', 'Journal'),
        ('litera', 'Litera'),
        ('lumen', 'Lumen'),
        ('lux', 'Lux'),
        ('materia', 'Materia'),
        ('minty', 'Minty'),
        ('morph', 'Morph'),
        ('pulse', 'Pulse'),
        ('quartz', 'Quartz'),
        ('sandstone', 'Sandstone'),
        ('simplex', 'Simplex'),
        ('sketchy', 'Sketchy'),
        ('slate', 'Slate'),
        ('solar', 'Solar'),
        ('spacelab', 'Spacelab'),
        ('superhero', 'Superhero'),
        ('united', 'United'),
        ('vapor', 'Vapor'),
        ('yeti', 'Yeti'),
        ('zephyr', 'Zephyr')
    ], default='darkly')
    submit = SubmitField('Save')


class EmptyForm(FlaskForm):
    submit = SubmitField('Salvar')


class PostForm(FlaskForm):
    titulo = StringField(_l('Título'), validators=[DataRequired()])
    post = TextAreaField(_l('Conteúdo'), validators=[DataRequired()])

    post_photo = FileField(_l('Foto de perfil'), validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], _l(
            'Only JPEG and PNG images are allowed.'))
    ])
    video = FileField('Video')
    submit = SubmitField(_l('Enviar'))


class QuizForm(FlaskForm):      
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(current_dir, 'static', 'data', 'csv', 'dados_rodada.csv')
    df = pd.read_csv(csv_path)

    df_6a_rodada = df.loc[df['rodada'] == '6ª']
    selecao = df.loc[df['rodada'] == '6ª', ['time1', 'time2']]

    # transformando a seleção em um dicionário
    selecao_dict = selecao.to_dict(orient='records')
    
    answer1 = RadioField(selecao_dict[1]['time1'] + ' e ' + selecao_dict[1]['time2'],
        choices=[
            ('1', selecao_dict[1]['time1']),
            ('2', 'Empate'),
            ('3', selecao_dict[1]['time2'])
        ],
        validators=[DataRequired()])
    answer2 = RadioField(selecao_dict[2]['time1'] + ' e ' + selecao_dict[2]['time2'],
        choices=[
            ('1', selecao_dict[2]['time1']),
            ('2', 'Empate'),
            ('3', selecao_dict[2]['time2'])
        ],

        validators=[DataRequired()])
    answer3 = RadioField(selecao_dict[3]['time1'] + ' e ' + selecao_dict[3]['time2'],
                         choices=[
        ('1', selecao_dict[3]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[3]['time2'])
    ],  validators=[DataRequired()])
    answer4 = RadioField(selecao_dict[4]['time1'] + ' e ' + selecao_dict[4]['time2'],
                         choices=[
        ('1', selecao_dict[4]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[4]['time2'])
    ],  validators=[DataRequired()])
    answer5 = RadioField(selecao_dict[5]['time1'] + ' e ' + selecao_dict[5]['time2'],
                         choices=[
        ('1', selecao_dict[5]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[5]['time2'])
    ],  validators=[DataRequired()])
    answer6 = RadioField(selecao_dict[6]['time1'] + ' e ' + selecao_dict[6]['time2'],
                         choices=[
        ('1', selecao_dict[6]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[6]['time2'])
    ],  validators=[DataRequired()])
    answer7 = RadioField(selecao_dict[7]['time1'] + ' e ' + selecao_dict[7]['time2'],
                         choices=[
        ('1', selecao_dict[7]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[7]['time2'])
    ],  validators=[DataRequired()])
    answer8 = RadioField(selecao_dict[8]['time1'] + ' e ' + selecao_dict[8]['time2'],
                         choices=[
        ('1', selecao_dict[8]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[8]['time2'])
    ],  validators=[DataRequired()])
    answer9 = RadioField(selecao_dict[9]['time1'] + ' e ' + selecao_dict[9]['time2'],
                         choices=[
        ('1', selecao_dict[9]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[9]['time2'])
    ],  validators=[DataRequired()])
    answer10 = RadioField(selecao_dict[0]['time1'] + ' e ' + selecao_dict[0]['time2'],
                          choices=[
        ('1', selecao_dict[0]['time1']),
        ('2', 'Empate'),
        ('3', selecao_dict[0]['time2'])
    ],  validators=[DataRequired()])
