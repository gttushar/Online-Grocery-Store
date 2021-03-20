from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Consumer(UserMixin, db.Model):
    username = db.Column(db.String(64), primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

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
