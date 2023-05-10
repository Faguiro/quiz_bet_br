from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, ValidationError
from flask_babel import _, lazy_gettext as _l
from bet.models import User
from wtforms import RadioField
from flask_wtf.file import FileField, FileAllowed


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
    answer1 = RadioField('Palmeira e Cuiabá', choices=[(
        '1', 'Palmeiras'), ('2', 'Empate'), ('3', 'Cuiabá')], validators=[DataRequired()])
    answer2 = RadioField('answer2', choices=[(
        '1', 'América'), ('2', 'Empate'), ('3', 'Fluminense')], validators=[DataRequired()])
    answer3 = RadioField('answer3', choices=[(
        '1', 'Botafogo'), ('2', 'Empate'), ('3', 'São Paulo')], validators=[DataRequired()])
    answer4 = RadioField('answer4', choices=[(
        '1', 'Bragantino'), ('2', 'Empate'), ('3', 'Bahia')], validators=[DataRequired()])
    answer5 = RadioField('answer5', choices=[(
        '1', 'Atlétio-PR'), ('2', 'Empate'), ('3', 'Goiás')], validators=[DataRequired()])
    answer6 = RadioField('answer6', choices=[(
        '1', 'Fortaleza'), ('2', 'Empate'), ('3', 'Internacional')], validators=[DataRequired()])
    answer7 = RadioField('answer6', choices=[(
        '1', 'Atético-MG'), ('2', 'Empate'), ('3', 'Vasco da Gama')], validators=[DataRequired()])
    answer8 = RadioField('answer6', choices=[(
        '1', 'Corinthians'), ('2', 'Empate'), ('3', 'Cruzeiro')], validators=[DataRequired()])
    answer9 = RadioField('answer6', choices=[(
        '1', 'Flamengo'), ('2', 'Empate'), ('3', 'Coritiba')], validators=[DataRequired()])
    answer10 = RadioField('answer6', choices=[(
        '1', 'Gêmio'), ('2', 'Empate'), ('3', 'Santos')], validators=[DataRequired()])
