from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Consumer(UserMixin, db.Model):
    cid = db.Column(db.integer,primary_key=True)
    username = db.Column(db.String(64), unique=True , nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(50),nullable=False)
    city_id = db.Column(db.String(5),db.Foreignkey('city.cityid'),nullable = False)

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
    return Consumer.query.get(username)

class Manager(UserMixin, db.Model):
    manager_id = db.Column(db.integer,primary_key=True)
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

class Deliviry_Agent(UserMixin, db.Model):
    agent_id = db.Column(db.integer,primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    city_id = db.Column(db.String(5),db.Foreignkey('city.cityid'),nullable = False)
    pending_deliveries = db.Column(db.integer,nullable=False)

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
    brand = db.Column(db.String(30),db.Foreignkey('Manager.brand'),nullable = False)
    avg_rating = db.Column(db.Float(precision=2),nullable=False)
    price = db.Column(db.Float(precision=5),nullable=False)
    quantity = db.Column(db.Float(precision=5),nullable=False)

class Order(db.Model):
    order_id = db.Column(db.Integer,primary_key=True)
    cid = db.Column(db.integer,db.ForeignKey('Consumer.cid'),nullable=False)
    amount = db.Column(db.Float(precision=5),nullable=False)
    status = db.Column(db.String(15),nullable=False)
    time_of_order = db.Column(db.datetime,nullable=False,default=datetime.utcnow)
    time_of_delivery = db.Column(db.datetime,nullable=False,default=datetime.utcnow)
    agent_id=db.Column(db.integer,db.ForeignKey('Delivery_Agent'),nullable=False)

class City(db.Model):
    city_id = db.Column(db.String(5),primary_key=True)
    city_name = db.Column(db.String(30),nullable=False)

class Contains(db.Model):
    order_id=db.Column(db.Integer,primary_key=True,db.ForeignKey('Order.order_id'))
    item_id=db.Column(db.Integer,primary_key=True,db.ForeignKey('Item.item_id'))
    quantity= db.Column(db.Float(precision=5),nullable=False)

class Item-city(db.Model):
    city_id=db.Column(db.String(5),primary_key=True,db.ForeignKey('City.city_id'))
    item_id=db.Column(db.Integer,primary_key=True,db.ForeignKey('Item.item_id'))
    quantity= db.Column(db.Float(precision=5),nullable=False)

class Review(db.Model):
    cid = db.Column(db.Integer,primary_key=True,db.ForeignKey('Consumer.cid'))
    item_id=db.Column(db.Integer,primary_key=True,db.ForeignKey('Item.item_id'))
    review = db.Column(db.String(100))
    rating = db.Column(db.Integer,nullable=False)
