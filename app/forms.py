from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, RadioField,DecimalField
from wtforms.validators import DataRequired,EqualTo,Length,Email,ValidationError, NumberRange
from app.models import Consumer, Manager, Delivery_agent

class LoginForm(FlaskForm):
	username=StringField('Username',validators=[DataRequired()])
	password=PasswordField('Password',validators=[DataRequired()])
	user_type=StringField('Sign in as',validators=[DataRequired()])
	submit=SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[ DataRequired() ])
    email=StringField('Email', validators=[ DataRequired(), Email() ])
    password=PasswordField('Password', validators=[ DataRequired(),Length(min=6) ])
    confirm_password=PasswordField('Confirm password', validators=[ DataRequired(),EqualTo('password') ])
    submit=SubmitField('Sign Up', validators=[ DataRequired() ])

class Consumer_Registration_Form(RegistrationForm,FlaskForm):
	# basic_details = RegistrationForm()
    city_id = StringField('City', validators=[ DataRequired(), Length(max=64)])
    address = StringField('Address', validators=[ DataRequired(), Length(max=128)])
    phone_no = StringField('Phone number', validators=[ DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Sign Up', validators=[ DataRequired() ])
    def validate_username(self,username):
        user=Consumer.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Consumer username already exists')

    def validate_phone_no(self, phone_no):
        if not phone_no.data.isnumeric():
            raise ValidationError('Invalid Phone Number')

    def validate_email(self,email):
        user=Consumer.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email id is already registered')

class Manager_Registration_Form(RegistrationForm,FlaskForm):
    # basic_details = RegistrationForm()
    brand = StringField('Brand', validators=[ DataRequired(), Length(max=30)])
    submit = SubmitField('Sign Up', validators=[ DataRequired() ])

    def validate_username(self,username):
        user=Manager.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Manager username already exists')

    def validate_email(self,email):
        user=Manager.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email id is already registered')

class Agent_Registration_Form(RegistrationForm,FlaskForm):
    # basic_details = RegistrationForm()
    city_id = StringField('City', validators=[ DataRequired(), Length(max=64)])
    submit = SubmitField('Sign Up', validators=[ DataRequired() ])

    def validate_username(self,username):
        user=Delivery_agent.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Delivery Agent username already exists')

    def validate_email(self,email):
        user=Delivery_agent.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email id is already registered')

class SearchForm(FlaskForm):
    category=RadioField('Search by',default='Product',choices=[('choice1','Brand'),('choice2','Product'),('choice3','Category')])
    search_text=StringField(None,validators=[DataRequired()])
    submit=SubmitField('Search')

class CheckoutForm(FlaskForm):
    cardno=StringField('Card no.',validators=[DataRequired()])
    cvv=IntegerField('CVV', validators=[DataRequired(),NumberRange(min=0,max=1000)])
    submit=SubmitField('Confirm Order')

class ItemaddForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired(),Length(max=50)])
    category = StringField('Category',validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired(),Length(max = 100)])
    price = DecimalField('Price',validators=[DataRequired()],places=2)

class Changequantityform(FlaskForm):
    quantity = IntegerField('Quantity',validators=[DataRequired(),NumberRange(min=0)])
