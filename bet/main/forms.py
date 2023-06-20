from flask import request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, ValidationError
from flask_babel import _, lazy_gettext as _l
from bet.models import User
from wtforms import RadioField
from flask_wtf.file import FileField, FileAllowed 
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





def create_quiz_form(selecao_dict):
    fields = {}

    for i, selecao in enumerate(selecao_dict):
        choices = [
            ('1', 'Vitória ' + selecao['time1']),
            ('2', 'Empate'),
            ('3', 'Vitória ' + selecao['time2'])
        ]

        field = RadioField(
            label=selecao['time1'] + ' e ' + selecao['time2'],
            choices=choices,
            validators=[DataRequired()]
        )

        fields['answer{}'.format(i)] = field

    QuizForm = type('QuizForm', (FlaskForm,), fields)
    return QuizForm()


    