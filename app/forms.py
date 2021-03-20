from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,EqualTo,Length,Email,ValidationError
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


