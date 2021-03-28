from app import db
from app import login
from app.routes import session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Consumer(UserMixin, db.Model):
    cid = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique=True , nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(128),nullable=False)
    city_id = db.Column(db.String(5),db.ForeignKey('city.city_id'),nullable = False)
    phone_no = db.Column(db.String(10), unique=True , nullable=False)

    def __repr__(self):
        return f"Consumer('{self.username}')"
    
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return self.username
    
@login.user_loader
def load_user(username):
    return Consumer.query.filter_by(username=username).first()

class Manager(UserMixin, db.Model):
    manager_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    brand = db.Column(db.String(30),nullable=False,unique=True)

    def __repr__(self):
        return f"Manager('{self.username}')"
    
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return self.username

class Delivery_agent(UserMixin, db.Model):
    agent_id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    city_id = db.Column(db.String(5),db.ForeignKey('city.city_id'),nullable = False)
    pending_deliveries = db.Column(db.Integer,nullable=False)

    def __repr__(self):
        return f"Delivery_Agent('{self.username}')"
    
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def get_id(self):
        return self.username

class Item(db.Model):
    item_id = db.Column(db.Integer,primary_key=True)
    category = db.Column(db.String(30),nullable=False)
    name = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(100))
    brand = db.Column(db.String(30),db.ForeignKey('manager.brand'),nullable = False)
    avg_rating = db.Column(db.Float(precision=2),nullable=False)
    price = db.Column(db.Float(precision=5),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    totalsold = db.Column(db.Integer,nullable=False)

class Order(db.Model):
    order_id = db.Column(db.Integer,primary_key=True)
    cid = db.Column(db.Integer,db.ForeignKey('consumer.cid'),nullable=False)
    amount = db.Column(db.Float(precision=5),nullable=False)
    status = db.Column(db.String(15),nullable=False)
    time_of_order = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    time_of_delivery = db.Column(db.DateTime,default=datetime.utcnow)
    agent_id=db.Column(db.Integer,db.ForeignKey('delivery_agent.agent_id'),nullable=False)

class City(db.Model):
    city_id = db.Column(db.String(5),primary_key=True)
    city_name = db.Column(db.String(30),nullable=False)

class Contains(db.Model):
    order_id=db.Column(db.Integer,db.ForeignKey('order.order_id'),primary_key=True)
    item_id=db.Column(db.Integer,db.ForeignKey('item.item_id'), primary_key=True)
    quantity= db.Column(db.Integer,nullable=False)

class Itemcity(db.Model):
    city_id=db.Column(db.String(5),db.ForeignKey('city.city_id'), primary_key=True)
    item_id=db.Column(db.Integer,db.ForeignKey('item.item_id'),primary_key=True)
    quantity= db.Column(db.Integer,nullable=False)

class Review(db.Model):
    cid = db.Column(db.Integer,db.ForeignKey('consumer.cid'),primary_key=True)
    item_id=db.Column(db.Integer,db.ForeignKey('item.item_id'),primary_key=True)
    review = db.Column(db.String(100))
    rating = db.Column(db.Integer,nullable=False)

class Cart(db.Model):
    cid = db.Column(db.Integer,db.ForeignKey('consumer.cid'),primary_key=True)
    item_id=db.Column(db.Integer,db.ForeignKey('item.item_id'),primary_key=True)
    quantity=db.Column(db.Integer,nullable=False)
    db.CheckConstraint('quantity>0','check1')
