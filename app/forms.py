from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, IntegerField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User, Product

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Rembember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    pincode = IntegerField('Pincode', validators=[DataRequired()])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('User Already exist!')
    
    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user is not None:
            raise ValidationError('User Already exist!')

class AddProductForm(FlaskForm):
    product_image = FileField('Product Image', validators=[DataRequired()])
    product_name = StringField('Product Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    discount_price = DecimalField('Discount Price')
    submit = SubmitField('Add Product')

    def validate_product_name(self, product_name):
        product = Product.query.filter_by(product_name=product_name.data).first()
        if product is not None:
            raise ValidationError('Use Different Product Name')

    def validate_product_image(self, product_image):
        if not ('.' in product_image.data.filename and \
            product_image.data.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS):
            raise ValidationError('Image type not valid')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

# class QuantityForm(FlaskForm):
#     quantity = IntegerField('Quantity')
#     submit = SubmitField('Submit')



        
    

    
    
