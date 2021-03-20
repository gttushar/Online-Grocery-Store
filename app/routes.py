from flask import render_template, redirect, url_for, flash, request, session
from app import app
from app import db

from app.forms import LoginForm, RegistrationForm
from app.models import Consumer
from flask_login import current_user,login_user, logout_user, login_required
from werkzeug.urls import url_parse

@app.route('/home')
@login_required
def home():
    return render_template('home.html',title='home')

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
        user=Consumer.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        session['username']=user.username
        session['user_type']='Consumer'
        login_user(user)
        flash('User successfully logged in')
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
    print(session['username'])
    logout_user()
    session.pop('username',None)
    session.pop('user_type',None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user = Consumer(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

