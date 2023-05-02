from bet import create_app, db, cli
from bet.models import User, Post, Quiz, Pagamento, Produto
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


from flask_admin import Admin, AdminIndexView
from flask_login import current_user
app = create_app()

cli.register(app)
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1 

admin = Admin(app, index_view=MyAdminIndexView())



class UserView(ModelView):
    column_searchable_list = ['username', 'email']
    column_filters = ['username']

class PostView(ModelView):
    column_searchable_list = ['user_id', 'body']
    column_filters = ['id']

class ProductView(ModelView):
    column_searchable_list = ['nome', 'preco','descricao','por' ]
    column_filters = ['nome']

class PagamentoView(ModelView):
    column_searchable_list = ['id','pagador','email' ]
    column_filters = ['id']
class QuizView(ModelView):
    column_searchable_list = ['id' ]
    column_filters = ['id']


admin.add_view(UserView(User, db.session))
admin.add_view(QuizView(Quiz, db.session))
admin.add_view(PagamentoView(Pagamento, db.session))
admin.add_view(ProductView(Produto, db.session))
admin.add_view(PostView(Post, db.session))


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Quiz': Quiz, 'Pagamento': Pagamento, 'Produto': Produto}
