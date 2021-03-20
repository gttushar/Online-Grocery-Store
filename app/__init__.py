from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager

app=Flask(__name__)
app.config['SECRET_KEY']='1234'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)
login=LoginManager(app)
login.login_view='login'

from app import routes,models
