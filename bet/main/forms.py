from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from bet.models import User
from wtforms import RadioField
from flask_wtf.file import FileField, FileAllowed



class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    profile_photo = FileField(_l('Profile Photo'), validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], _l('Only JPEG and PNG images are allowed.'))
    ])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class QuizForm(FlaskForm):
    answer1 = RadioField('answer1', choices=[('1', 'Palmeiras'), ('2', 'Empate'), ('3', 'Cuiabá')], validators=[DataRequired()])
    answer2 = RadioField('answer2', choices=[('1', 'América'), ('2', 'Empate'), ('3', 'Fluminense')], validators=[DataRequired()])
    answer3 = RadioField('answer3', choices=[('1', 'Botafogo'), ('2', 'Empate'), ('3', 'São Paulo')], validators=[DataRequired()])
    answer4 = RadioField('answer4', choices=[('1', 'Bragantino'), ('2', 'Empate'), ('3', 'Bahia')], validators=[DataRequired()])
    answer5 = RadioField('answer5', choices=[('1', 'Atlétio-PR'), ('2', 'Empate'), ('3', 'Goiás')], validators=[DataRequired()])
    answer6 = RadioField('answer6', choices=[('1', 'Fortaleza'), ('2', 'Empate'), ('3', 'Internacional')], validators=[DataRequired()])
    answer7 = RadioField('answer6', choices=[('1', 'Atético-MG'), ('2', 'Empate'), ('3', 'Vasco da Gama')], validators=[DataRequired()])
    answer8 = RadioField('answer6', choices=[('1', 'Corinthians'), ('2', 'Empate'), ('3', 'Cruzeiro')], validators=[DataRequired()])
    answer9 = RadioField('answer6', choices=[('1', 'Flamengo'), ('2', 'Empate'), ('3', 'Coritiba')], validators=[DataRequired()])
    answer10 = RadioField('answer6',choices=[('1', 'Gêmio'), ('2', 'Empate'), ('3', 'Santos')], validators=[DataRequired()])