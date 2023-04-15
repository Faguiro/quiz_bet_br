from bet import create_app, db, cli
from bet.models import User, Post, Pagamento, Quiz

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Pagamento': Pagamento,'Quiz': Quiz}
