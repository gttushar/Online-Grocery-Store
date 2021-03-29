from flask import render_template, redirect, url_for, flash, request, session, abort
import sqlalchemy
from sqlalchemy import func
from sqlalchemy import text, and_
from app import app
from app import db
import sys

from app.forms import *
from app.models import *
from flask_login import current_user,login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/consumer_home',methods = ['GET','POST'])
@login_required
def consumer_home():
	#print(session['user_type'], " Home : ", session['username'], file=sys.stderr)
	if(session['user_type']!='Consumer'):
		abort(403)
	page=request.args.get('page',1,type=int)
	item_list = None
	form = SearchForm()
	if request.method == 'POST':
		if form.category.data == "Brand":
			item_list = Item.query.filter_by(brand = form.search_text.data)\
				.order_by(Item.totalsold.desc())\
				.paginate(page=page,per_page=200)
			return render_template('consumer_home.html',title='home',form=form,item_list=item_list)
		if form.category.data == "Product":
			item_list = Item.query.filter_by(name = form.search_text.data)\
				.order_by(Item.totalsold.desc())\
				.paginate(page=page,per_page=200)
			return render_template('consumer_home.html',title='home',form=form,item_list=item_list)
		if form.category.data == "Category":
			item_list = Item.query.filter_by(category = form.search_text.data)\
				.order_by(Item.totalsold.desc())\
				.paginate(page=page,per_page=200)
			return render_template('consumer_home.html',title='home',form=form,item_list=item_list)
	item_list = Item.query.order_by(Item.totalsold.desc()).paginate(page=page,per_page=20)
	return render_template('consumer_home.html',title='home',form=form,item_list=item_list)

@app.route('/manager_home',methods = ['GET','POST'])
@login_required
def manager_home():
	if(session['user_type']!='Manager'):
		abort(403)
	curr_manager= Manager.query.filter_by(manager_id = session['userid']).first()
	brand = curr_manager.brand
	page = request.args.get('page',1,type = int)
	item_list = Item.query.filter_by(brand = brand).paginate(page = page,per_page = 20)
	return render_template('manager_home.html',title = 'home',item_list = item_list,brand =brand)

@app.route('/manager_add_item',methods = ['GET','POST'])
@login_required
def manager_add_item():
	if(session['user_type']!='Manager'):
		abort(403)
	form=ItemaddForm()
	if form.validate_on_submit():
		curr_manager= Manager.query.filter_by(manager_id = session['userid']).first()
		brand = curr_manager.brand
		item = Item(name=form.name.data, category=form.category.data, 
						description=form.description.data, price=form.price.data,brand = brand,totalsold=0,quantity=0)
		count=db.session.query(func.count('*')).select_from(Item).scalar()
		item.item_id=count+1
		db.session.add(item)
		Citylist = City.query.all()
		for city in Citylist:
			itemcity = Itemcity(item_id=item.item_id,city_id=city.city_id,quantity=0)
			db.session.add(itemcity)
		db.session.commit()
		return redirect(url_for('manager_home'))
	return render_template('manager_add_item.html', title='Add Item', form=form)

@app.route('/manager/<int:item_id>')
@login_required
def manager_item(item_id):
	if(session['user_type']!='Manager'):
		abort(403)
	item = Item.query.filter_by(item_id = item_id).first_or_404();
	itemcity = Itemcity.query.join(City,City.city_id==Itemcity.city_id)\
					.add_columns(Itemcity.city_id,Itemcity.quantity,City.city_name)\
					.order_by(Itemcity.quantity.desc())\
					.filter(Itemcity.item_id == item_id)
	return render_template('manager_view_item.html',title ='View Item',item=item,itemcity = itemcity)

@app.route('/manager/<int:item_id>/<string:city_id>',methods=['GET','POST'])
@login_required
def quantity_change(item_id,city_id):
	if(session['user_type']!='Manager'):
		abort(403)
	curr_manager=Manager.query.filter_by(manager_id = session['userid']).first()
	item = Item.query.filter_by(item_id = item_id).first()
	if(curr_manager.brand != item.brand):
		flash("Invalid Access",'danger')
		return redirect(url_for(manager_home))
	form = Changequantityform();
	if form.validate_on_submit():
		itemcity = Itemcity.query.filter_by(item_id=item_id,city_id=city_id).first()
		itemcity.quantity +=form.quantity.data
		item.quantity +=form.quantity.data
		db.session.commit()
		return redirect("/manager_home")
	return render_template("add_quantity.html",item=item,city_id=city_id,form=form)

@app.route('/login',methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		if session['user_type'] == "Consumer":
			return redirect(url_for('consumer_home'))
		elif session['user_type'] == "Manager":
			return redirect(url_for('manager_home'))
		else:
			return redirect(url_for('agent_home'))
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
			flash('Invalid username or password','danger')
			return redirect(url_for('login'))

		session['username']=user.username
		session['user_type']=form.user_type.data
		if form.user_type.data == "Consumer":
			session['userid']=user.cid 
		elif form.user_type.data == "Manager":
			session['userid']=user.manager_id
		else:
			session['userid']=user.agent_id
		login_user(user)
		flash('User successfully logged in','success')
		print(form.user_type.data + " successfully logged in", file=sys.stderr)
		next_page=request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			if session['user_type']=='Consumer':
				next_page = url_for('consumer_home')
			elif session['user_type']=='Manager':
				next_page=url_for('manager_home')
			else:
				next_page=url_for('agent_home')
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
		if session['user_type'] == "Consumer":
			return redirect(url_for('consumer_home'))
		elif session['user_type'] == "Manager":
			return redirect(url_for('manager_home'))
		else:
			return redirect(url_for('agent_home'))
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
		flash('Congratulations, you are now a registered consumer!','success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/register_manager', methods=['GET', 'POST'])
def register_manager():
	if current_user.is_authenticated:
		if session['user_type'] == "Consumer":
			return redirect(url_for('consumer_home'))
		elif session['user_type'] == "Manager":
			return redirect(url_for('manager_home'))
		else:
			return redirect(url_for('agent_home'))
	form=Manager_Registration_Form()
	if form.validate_on_submit():
		# cid, username, email, password_hash, brand
		user = Manager(username=form.username.data, email=form.email.data, brand=form.brand.data)
		user.set_password(form.password.data)
		count=db.session.query(func.count('*')).select_from(Manager).scalar()
		user.manager_id=count+1
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered manager!','success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/register_agent', methods=['GET', 'POST'])
def register_agent():
	if current_user.is_authenticated:
		if session['user_type'] == "Consumer":
			return redirect(url_for('consumer_home'))
		elif session['user_type'] == "Manager":
			return redirect(url_for('manager_home'))
		else:
			return redirect(url_for('agent_home'))
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
		flash('Congratulations, you are now a registered delivery agent!','success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/view_cart')
@login_required
def view_cart():
    if(session['user_type']!='Consumer'):
        abort(403)
    cart_list=Cart.query.join(Item,Cart.item_id==Item.item_id)\
        .add_columns(Item.item_id,Item.name,Item.brand,Cart.quantity,Item.price)\
            .filter(Cart.cid==session['userid'])
    return render_template('view_cart.html',title='Cart',cart=cart_list)

def place_order(cart_list):
    x=Consumer.query.filter_by(Consumer.cid==session['userid'])
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
    
    order1=Order(order_id=order_id,cid=session['userid'],amount=amount,status='Order placed',\
        time_of_order=datetime.utcnow,time_of_delivery=None,agent_id=agent.agent_id)
    

@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
	if(session['user_type']!='Consumer'):
		abort(403)

	amount=0
	form=CheckoutForm()
	cart_list=Cart.query.join(Item,Cart.item_id==Item.item_id)\
		.filter(Cart.cid==session['userid'])\
			.add_columns(Item.item_id,Item.name,Item.brand,Cart.quantity,Item.price)
	for x in cart_list:
		amount+=x.quantity*x.price
	if form.validate_on_submit():
		place_order(cart_list)
		for x in cart_list:
			db.session.delete(x)
		db.session.commit()
		flash('Your order has been placed successfully','success')
		return redirect(url_for('consumer_home'))
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

@app.route("/view_item/<int:item_id>")
@login_required
def view_item(item_id):
	if(session['user_type']!='Consumer'):
		abort(403)
	item=Item.query.get_or_404(item_id)
	x=Cart.query.filter(and_(Cart.cid==session['userid'],Cart.item_id==item.item_id)).first()
	count=0
	if x is not None:
		count=x.quantity
	return render_template('view_item.html',item=item,count=count)

@app.route("/cart_add/<int:item_id>")
@login_required
def cart_add(item_id,count):
	if(session['user_type']!='Consumer'):
		abort(403)
	item=Item.query.get_or_404(item_id)
	if count>0:
		cart_item=Cart.query.filter(and_(Cart.cid==session['userid'],Cart.item_id==item_id)).first()
		cart_item.quantity+=1
		db.session.commit()
	else:
		x=Cart(cid=session['userid'],item_id=item.item_id,quantity=1)
		db.session.add(x)
		db.session.commit()
	return redirect(url_for('view_item'),item_id=item_id)

@app.route("/cart_remove/<int:item_id>")
@login_required
def cart_remove(item_id,count):
	if(session['user_type']!='Consumer'):
		abort(403)
	item=Item.query.get_or_404(item_id)
	cart_item=Cart.query.filter(and_(Cart.cid==session['userid'],Cart.item_id==item_id)).first()
	if count>1:
		cart_item.quantity-=1
		db.session.commit()
	else:
		db.session.delete(cart_item)
		db.session.commit()
	return redirect(url_for('view_item'),item_id=item_id)

@app.route('/agent_home',methods = ['GET','POST'])
@login_required
def agent_home():
	if(session['user_type']!='Delivery_agent'):
		abort(403)
	# agent = Delivery_agent.query.filter_by(agent_id = session['userid']).first()
	pending_orders = []
	for order_object in Order.query.filter_by(agent_id = session['userid'], status = "DELIVERING").all():
		order = {}
		order['order_id'] = order_object.order_id
		order['consumer_name'] = Consumer.query.filter_by(cid=order_object.cid).first().username
		order['amount'] = order_object.amount
		order['status'] = order_object.status
		order['time_of_order'] = order_object.time_of_order
		order['time_of_delivery'] = order_object.time_of_delivery
		contains = Contains.query.filter_by(order_id = order['order_id']).all()
		# Items in order
		order['contains'] = []
		for item in contains:
			item_details = Item.query.filter_by(item_id=item.item_id).first()
			order['contains'].append({'item_id':item.item_id, 'item_name':item_details.name, \
									  'quantity':item.quantity, 'price':item_details.price})

		pending_orders.append(order)
	return render_template('agent_home.html',title = 'home', pending_orders = pending_orders)


@app.route('/completed_orders/<int:agent_id>')
@login_required
def completed_orders(agent_id):
	if(session['user_type']!='Delivery_agent'):
		abort(403)
	completed_orders = []
	for order_object in Order.query.filter_by(agent_id = agent_id, status = "COMPLETE").all():
		order = {}
		order['order_id'] = order_object.order_id
		order['consumer_name'] = Consumer.query.filter_by(cid=order_object.cid).first().username
		order['amount'] = order_object.amount
		order['status'] = order_object.status
		order['time_of_order'] = order_object.time_of_order
		order['time_of_delivery'] = order_object.time_of_delivery
		contains = Contains.query.filter_by(order_id = order['order_id']).all()
		# Items in order
		order['contains'] = []
		for item in contains:
			item_details = Item.query.filter_by(item_id=item.item_id).first()
			order['contains'].append({'item_id':item.item_id, 'item_name':item_details.name, \
									  'quantity':item.quantity, 'price':item_details.price})

		completed_orders.append(order)
	return render_template('completed_orders.html', completed_orders = completed_orders)

@app.route('/mark_order_delivered/<int:order_id>')
@login_required
def mark_order_delivered(order_id):
	if(session['user_type']!='Delivery_agent'):
		abort(403)
	order = Order.query.filter_by(order_id = order_id).first()
	if order.status == 'COMPLETE':
		flash('Order id = ' + str(order_id) + ' is already delivered !!', 'danger')
	elif order.status == 'DELIVERING':
		order.status = 'COMPLETE'
		db.session.commit()
		flash('Order id = ' + str(order_id) + ' marked as DELIVERED ', 'success')
	return redirect(url_for('agent_home'))

@app.route('/view_order/<int:order_id>')
@login_required
def view_order(order_id):
	if(session['user_type']!='Consumer'):
		abort(403)
	order_list=Contains.query.join(Item,Item.item_id==Contains.item_id)\
		.filter(Contains.order_id==order_id)\
			.add_columns(Item.name,Item.brand,Item.price)
	return render_template('consumer_view_order.html',order_list=order_list)
