from flask import render_template, redirect, url_for, flash, request, session, abort
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import text
from app import app
from app import db

from app.forms import *
from app.models import *
from flask_login import current_user,login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

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

        session['cid']=user.cid
        session['user_type']='Consumer'
        login_user(user)
        flash('User successfully logged in')
        return redirect(url_for('home'))
    return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
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
        count=db.session.query(func.count('*')).select_from(Consumer).scalar()
        user.cid=count+1
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/view_cart')
@login_required
def view_cart():
    if(session['user_type']!='Consumer'):
        abort(403)
    cart_list=Cart.query.join(Item,Cart.item_id==Item.item_id)\
        .add_columns(Item.item_id,Item.name,Item.brand,Cart.quantity,Item.price)\
            .filter(Cart.cid==session['user'])
    return render_template('view_cart.html',title='Cart',cart=cart_list)

def place_order(cart_list):
    x=Consumer.query.filter_by(Consumer.cid==session['cid'])
    order_id=db.session.query(func.count('*')).select_from(Order).scalar()
    order_id+=1
    min_count=db.session.query(func.min('pending_deliveries')).select_from('Delivery_agent').scalar()
    agent=Delivery_agent.query.filter(Delivery_agent.pending_deliveries==min_count).first()
    amount=0

    for y in cart_list: 
        z=Itemcity.query.filter(Itemcity.city_id==x.city_id,Itemcity.item_id==y.item_id)
        z.quantity-=y.quantity
        db.session.commit()
        order_item=Contains(order_id=order_id,item_id=y.item_id,quantity=y.quantity)
        db.session.add(order_item)
        db.session.commit()
        amount+=y.price*y.quantity
    
    order1=Order(order_id=order_id,cid=session['cid'],amount=amount,status='Order placed',\
        time_of_order=datetime.utcnow,time_of_delivery=None,agent_id=agent.agent_id)
    

@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    if(session['user_type']!='Consumer'):
        abort(403)
    form=CheckoutForm()
    cart_list=Cart.query.join(Item,Cart.item_id==Item.item_id)\
        .add_columns(Item.item_id,Item.name,Item.brand,Cart.quantity,Item.price)
    if form.validate_on_submit():
        place_order(cart_list)
        flash('Your order has been placed successfully')
        return redirect(url_for('home'))
    return render_template('checkout.html',title='Checkout',cart=cart_list)
