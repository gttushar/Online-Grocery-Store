from flask import render_template, redirect, url_for, flash, request, session, abort
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import text
from app import app
from app import db
import sys

from app.forms import *
from app.models import *
from flask_login import current_user,login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/home',methods=['GET','POST'])
@login_required
def home():
	form=SearchForm()
	return render_template('home.html',title='home')

@app.route('/login',methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=LoginForm()
	if form.validate_on_submit():
		user=None
		if form.user_type.data == "Consumer":
			user=Consumer.query.filter_by(username=form.username.data).first()
			# print("Consumer logged in", file=sys.stderr)
		elif form.user_type.data == "Manager":
			user=Manager.query.filter_by(username=form.username.data).first()
		elif form.user_type.data == "Delivery_agent":
			user=Delivery_agent.query.filter_by(username=form.username.data).first() 
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))

		session['username']=user.username
		session['user_type']=form.user_type.data
		login_user(user)
		flash('User successfully logged in')
		print(form.user_type.data + " successfully logged in", file=sys.stderr)
		next_page=request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('home')
		return redirect(next_page)
	return render_template('login.html',title='Sign In',form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('username',None)
    session.pop('user_type',None)
    return redirect(url_for('login'))

@app.route('/view_profile')
@login_required
def view_profile():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	user_type = session['user_type']
	username  = session['username']
	if user_type == "Consumer":
		user = Consumer.query.filter_by(username=username).first()
	elif user_type == "Manager":
		user = Manager.query.filter_by(username=username).first()
	elif user_type == "Delivery_agent":
		user = Delivery_agent.query.filter_by(username=username).first() 
	return render_template('view_profile.html', user = user, user_type = user_type)

@app.route('/register_consumer', methods=['GET', 'POST'])
def register_consumer():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=Consumer_Registration_Form()
	if form.validate_on_submit():
		# cid, username, email, password_hash, address, city_id, phone_no
		user = Consumer(username=form.username.data, email=form.email.data, 
						address=form.address.data, city_id=form.city_id.data, phone_no=form.phone_no.data)
		user.set_password(form.password.data)
		count=db.session.query(func.count('*')).select_from(Consumer).scalar()
		user.cid=count+1
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered consumer!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/register_manager', methods=['GET', 'POST'])
def register_manager():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=Manager_Registration_Form()
	if form.validate_on_submit():
		# cid, username, email, password_hash, brand
		user = Manager(username=form.username.data, email=form.email.data, brand=form.brand.data)
		user.set_password(form.password.data)
		count=db.session.query(func.count('*')).select_from(Manager).scalar()
		user.manager_id=count+1
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered manager!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/register_agent', methods=['GET', 'POST'])
def register_agent():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form=Agent_Registration_Form()
	if form.validate_on_submit():
		# cid, username, email, password_hash, city_id
		user = Delivery_agent(username=form.username.data, email=form.email.data, city_id=form.city_id.data)
		user.set_password(form.password.data)
		count=db.session.query(func.count('*')).select_from(Delivery_agent).scalar()
		user.agent_id=count+1
		user.pending_deliveries=0
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered delivery agent!')
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

	amount=0
	form=CheckoutForm()
	cart_list=Cart.query.join(Item,Cart.item_id==Item.item_id)\
		.add_columns(Item.item_id,Item.name,Item.brand,Cart.quantity,Item.price)
	for x in cart_list:
		amount+=x.quantity*x.price
	if form.validate_on_submit():
		place_order(cart_list)
		flash('Your order has been placed successfully')
		return redirect(url_for('home'))
	return render_template('checkout.html',title='Checkout',cart=cart_list,amount=amount)

@app.route('/orders')
def orders():
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	if(session['user_type']!='Consumer'):
		abort(403)
	username  = session['username']
	cid = Consumer.query.filter_by(username=username).first().cid
	print(Order.query.filter_by(cid=cid).all(), file=sys.stderr)
	orders = []
	for order_object in Order.query.filter_by(cid=cid).all():
		order = {}
		order['order_id'] = order_object.order_id
		order['amount'] = order_object.amount
		order['status'] = order_object.status
		order['time_of_order'] = order_object.time_of_order
		order['time_of_delivery'] = order_object.time_of_delivery
		order['agent_name'] = Delivery_agent.query.filter_by(agent_id=order_object.agent_id).first().username
		contains = Contains.query.filter_by(order_id = order['order_id']).all()
		# Items in order
		order['contains'] = []
		for item in contains:
			item_name = Item.query.filter_by(item_id=item.item_id).first().name
			order['contains'].append({'item_id':item.item_id, 'item_name':item_name, 'quantity':item.quantity})

		orders.append(order)
	return render_template('orders.html', orders = orders)