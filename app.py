from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import SQLAlchemyUserDatastore, Security, current_user
from flask import  redirect, url_for, request
from flask_admin import Admin, AdminIndexView




app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)



from models import *

# Доступ к админке

class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


# Класс создания слага (человекопободнойссылки)
class BaseModeView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super(BaseModeView, self).on_model_change(form, model, is_created)


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass



class PostAdminView(AdminMixin, BaseModeView):
    form_columns = ['title', 'body', 'tags']


class TagAdminView(AdminMixin, BaseModeView):
    form_columns = ['name', 'posts']



admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='Home'))  # Подключили админку
admin.add_view(PostAdminView(Post, db.session))
admin.add_view(TagAdminView(Tag, db.session))



# Создаем user
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
