from bet import create_app, db, cli
from bet.models import User, Post, Quiz, Pagamento, Produto

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Quiz': Quiz, 'Pagamento': Pagamento, 'Produto': Produto}
