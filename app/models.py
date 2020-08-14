from datetime import datetime
from time import time
import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.Integer, unique=True)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(256))
    city = db.Column(db.String(32))
    state = db.Column(db.String(32))
    pincode = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users, 
        backref=db.backref('users', lazy='dynamic'))
    orders = db.relationship('Product', secondary='order', backref=db.backref('buyers', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password) 

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return f'<User {self.username}'

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(40), unique=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(256), unique=True)
    description = db.Column(db.String(500))
    category = db.Column(db.String(64))
    price = db.Column(db.Float(16))
    discount_price = db.Column(db.Float(16))
    product_image = db.Column(db.String)
    
    def __repr__(self):
        return f'Product {self.product_name}'
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    ordered = db.Column(db.Boolean, default=False)
    ordered_date = db.Column(db.DateTime, index=True, default=None)
    quantity = db.Column(db.Integer, default=1)
    amount_to_be_paid = db.Column(db.Float)

    def get_quantity(self):
        return self.quantity

    def set_quantity(self, quantity):
        self.quantity = quantity


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


