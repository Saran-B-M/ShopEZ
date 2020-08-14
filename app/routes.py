from flask import render_template, flash, redirect, request, url_for, send_file
from flask_login import current_user, login_user, logout_user, login_required
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import base64
from datetime import datetime

from app.forms import LoginForm, RegistrationForm, AddProductForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Product, Order, Role
from app import app, db

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            flag = 0
            for role in current_user.roles:
                if 'admin' in role.name:
                    flag = 1
            return flag
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class MyModelView(ModelView):
    can_create = False 
    def is_accessible(self):
        if current_user.is_authenticated:
            flag = 0
            for role in current_user.roles:
                if 'admin' in role.name:
                    flag = 1
            return flag 

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class OrdersView(BaseView):
    @expose('/')
    def index(self):
        orders = Order.query.order_by(Order.ordered_date.desc()).all()
        return self.render('admin/orders.html', orders=orders, Product=Product, User=User)

@app.route('/')
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(
        page, app.config['PRODUCTS_PER_PAGE'], False)
    next_url = url_for('home', page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('home', page=products.prev_num) \
        if products.has_prev else None
    return render_template('home.html', title='Home', 
        products=products.items, next_url=next_url, prev_url=prev_url, page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Email/Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

db.create_all()

if not User.query.filter(User.email == 'admin@shopez.com').first():
    user = User(
        username = 'admin',
        email = 'admin@shopez.com'
    )
    user.set_password('password')
    user.roles.append(Role(name='admin'))
    db.session.add(user)
    db.session.commit()

@app.route('/create-account', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
            phone=form.phone.data, address=form.address.data,
            city=form.city.data, state=form.state.data, pincode=form.pincode.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account Created!, Login to Continue!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Create Account', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/add-product', methods=['GET', 'POST'])
@login_required
def addProduct():
    flag = 0
    for role in current_user.roles:
        if 'admin' in role.name:
            flag = 1
    if flag == 0:
        flash('You are not authorized to access this page')
        return redirect(url_for('home'))
    form = AddProductForm()
    if form.validate_on_submit():
        product = Product(product_name=form.product_name.data, description=form.description.data,
                category=form.category.data.lower(), price=form.price.data, discount_price=form.discount_price.data)  
        product_image = request.files['product_image']
        product_image =  base64.b64encode(product_image.read()).decode('utf-8')
        product.product_image = product_image   
        db.session.add(product)
        db.session.commit()
        flash('Product added')
        redirect(url_for('home'))
    return render_template('add-product.html', title='Add Product', form=form)

@app.route('/product/<product_id>')
def product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    return render_template('product.html', title=product.product_name, product=product)

@app.route('/add-to-cart/<product_id>')
@login_required
def addToCart(product_id):
    product = Product.query.filter_by(id=product_id).first()
    order = Order.query.filter(Order.user_id==current_user.id, Order.product_id==product.id, Order.ordered==False).first()
    if order is None:
        order = Order(user_id=current_user.id, product_id=product_id)
        db.session.add(order)
        flash('Item Added to Cart!')
        db.session.commit()
        return redirect(url_for('product', product_id=product_id))
    else:
        flash('Item Already in Cart')
        return redirect(url_for('home'))

@app.route('/increase-quantity/<product_id>')
def increase_quantity(product_id):
    order = Order.query.filter(Order.user_id==current_user.id, Order.product_id==product_id, Order.ordered==False).first()
    if order:
        quantity = order.get_quantity()
        quantity += 1
        order.set_quantity(quantity)
        db.session.commit()
        flash('Item Updated!')
        return redirect(url_for('cart'))
    
@app.route('/cart')
@login_required
def cart():
    orders =  Order.query.filter(Order.user_id==current_user.id, Order.ordered==False).all()
    cart_items, total_price = get_items(orders)
    return render_template('cart.html', title='Cart', cart_items=cart_items, total_price=total_price, Order=Order)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = EmptyForm()
    orders =  Order.query.filter(Order.user_id==current_user.id, Order.ordered==False).all()
    cart_items, total_price = get_items(orders)
    if not cart_items:
        flash('You have no items in Your Cart')
        return redirect('home')
    if form.validate_on_submit():
        for order in orders:
            order.ordered = True
            order.ordered_date = datetime.utcnow()
            product = Product.query.filter_by(id=order.id).first()
            if product:
                if product.discount_price is not None:
                    order.amount_to_be_paid = Product.query.filter_by(id=order.id).first().discount_price*order.get_quantity()
                else:
                    order.amount_to_be_paid = Product.query.filter_by(id=order.id).first().price*order.get_quantity()            
            db.session.commit()
        flash('Order Successfully Placed')
        return redirect(url_for('home'))
    return render_template('checkout-page.html', title='CheckOut', cart_items=cart_items, total_price=total_price, form=form)

def get_items(orders):
    items = []
    total_price = 0
    for order in orders:
        product = Product.query.filter_by(id=order.product_id).first()
        items.append(product)
        if product.discount_price:
            total_price += product.discount_price*order.quantity
        else:
            total_price += product.price*order.quantity
    return items, total_price

@app.route('/your-orders')
@login_required
def orders():
    orders = Order.query.filter(Order.user_id==current_user.id, Order.ordered==True).order_by(Order.ordered_date.desc()).all()
    ordered_items, price = get_items(orders)
    return render_template('your_orders.html', title='Your Orders', ordered_items=ordered_items, Order=Order)
    
@app.route('/category/<category>')
def show_by_category(category):
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category=category).paginate(
        page, app.config['PRODUCTS_PER_PAGE'], False)
    next_url = url_for('show_by_category', category=category, page=products.next_num) \
        if products.has_next else None
    prev_url = url_for('show_by_category', category=category, page=products.prev_num) \
        if products.has_prev else None
    return render_template('home.html', title=category, 
        products=products.items, next_url=next_url, prev_url=prev_url, page=page)

@app.route('/cart-remove-single-item/<product_id>')
@login_required
def cart_remove_single_item(product_id):
    product = Product.query.filter_by(id=product_id).first()
    order = Order.query.filter(Order.user_id==current_user.id, Order.product_id==product.id, Order.ordered==False).first()
    order.quantity -= 1
    if order.quantity == 0:
        return redirect(url_for('cart_remove_item', product_id=product_id))
    flash('Item Updated!')
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart-remove-item/<product_id>')
@login_required
def cart_remove_item(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product:
        order = Order.query.filter(Order.user_id==current_user.id, Order.product_id==product.id, Order.ordered==False).first()
        if order:
            db.session.delete(order)
            db.session.commit()
            flash('Item removed from Cart')
    return redirect(url_for('cart'))

@app.route('/cancel-order/<product_id>')
@login_required
def cancel_order(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if product:
        order = Order.query.filter(Order.user_id==current_user.id, Order.product_id==product.id, Order.ordered==True).first()
        if order:
            db.session.delete(order)
            db.session.commit()
            flash('Order canceled')
    return redirect(url_for('orders'))


