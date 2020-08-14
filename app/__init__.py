from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_mail import Mail
from flask_moment import Moment

from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
moment = Moment(app)

from app import routes, models

admin = Admin(app, index_view=routes.MyAdminIndexView(), template_mode='bootstrap3')

admin.add_view(routes.MyModelView(models.User, db.session))
admin.add_view(routes.MyModelView(models.Product, db.session))

admin.add_view(routes.OrdersView(name='Orders', endpoint='orders'))