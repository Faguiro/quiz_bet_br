from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from bet import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    profile_photo = db.Column(db.LargeBinary, nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    answers = db.relationship('Quiz', backref='user', lazy='dynamic')
    cateira = db.relationship('Pagamento', backref='user', lazy='dynamic')
    saldo = db.Column(db.Float, nullable=False, default=0.0)

    def atualiza_saldo(self, valor):
        self.saldo += valor # Atualiza o saldo do usuário com o valor recebido


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer1 = db.Column(db.String(255), nullable=False)
    answer2 = db.Column(db.String(255), nullable=False)
    answer3 = db.Column(db.String(255), nullable=False)
    answer4 = db.Column(db.String(255), nullable=False)
    answer5 = db.Column(db.String(255), nullable=False)
    answer6 = db.Column(db.String(255), nullable=False)
    answer7 = db.Column(db.String(255), nullable=False)
    answer8 = db.Column(db.String(255), nullable=False)
    answer9 = db.Column(db.String(255), nullable=False)
    answer10 = db.Column(db.String(255), nullable=False)
    answered = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Quiz {}>'.format(self.user_id)

class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pagador = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    preco = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    por = db.Column(db.String(50))
    ajustavel_quantidade = db.Column(db.Boolean)
    quantidade_minima = db.Column(db.Integer)
    quantidade_maxima = db.Column(db.Integer)