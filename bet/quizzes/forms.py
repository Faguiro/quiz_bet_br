from flask import request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, ValidationError
from flask_babel import _, lazy_gettext as _l
from bet.models import User
from wtforms import RadioField
from flask_wtf.file import FileField, FileAllowed 
import os



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


    