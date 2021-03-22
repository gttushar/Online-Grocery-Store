from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired,EqualTo,Length,Email,ValidationError, NumberRange
from app.models import Consumer

class LoginForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired()])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[ DataRequired() ])
    email=StringField('Email', validators=[ DataRequired(), Email() ])
    password=PasswordField('Password', validators=[ DataRequired(),Length(min=6) ])
    confirm_password=PasswordField('Confirm password', validators=[ DataRequired(),EqualTo('password') ])
    submit=SubmitField('Sign Up', validators=[ DataRequired() ])

    def validate_username(self,username):
        user=Consumer.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists')
    
    def validate_email(self,email):
        user=Consumer.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email id is already registered')

class Consumer_Registration_Form(RegistrationForm,FlaskForm):
	# basic_details = RegistrationForm()
	city_id = StringField('City', validators=[ DataRequired(), Length(max=64)])
	address = StringField('Address', validators=[ DataRequired(), Length(max=128)])
	phone_no = StringField('Phone number', validators=[ DataRequired(), Length(min=10, max=10)])
	submit = SubmitField('Sign Up', validators=[ DataRequired() ])

	def validate_phone_no(self, phone_no):
		print(type(phone_no.data))
		if not phone_no.data.isnumeric():
			raise ValidationError('Invalid Phone Number')

class Manager_Registration_Form(RegistrationForm,FlaskForm):
	# basic_details = RegistrationForm()
	brand = StringField('City', validators=[ DataRequired(), Length(max=30)])
	submit = SubmitField('Sign Up', validators=[ DataRequired() ])

class Agent_Registration_Form(RegistrationForm,FlaskForm):
	# basic_details = RegistrationForm()
	city_id = StringField('City', validators=[ DataRequired(), Length(max=64)])
	submit = SubmitField('Sign Up', validators=[ DataRequired() ])

class SearchForm(FlaskForm):
    search_text=TextAreaField(None,validators=[DataRequired()])
    submit=SubmitField('Search')

class CheckoutForm(FlaskForm):
    cardno=StringField('Card no.',validators=[DataRequired()])
    cvv=IntegerField('CVV', validators=[DataRequired(),NumberRange(min=0,max=1000)])
    submit=SubmitField('Confirm Order')
