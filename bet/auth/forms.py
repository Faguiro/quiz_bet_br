from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from bet.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Nome de usuário'), validators=[DataRequired()])
    password = PasswordField(_l('Senha'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Lembre de mim'))
    submit = SubmitField(_l('Entrar'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Nome de usuário'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repita a senha'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Registro'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Use um nome de usuário diferente.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Por favor, use um endereço de e-mail diferente.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Solicitar redefinição de senha'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Senha'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repita a senha'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Solicitar redefinição de senha'))
