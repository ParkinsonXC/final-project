from hashutils import make_pw_hash, check_pw_hash
from app import db
from datetime import datetime, date


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120)) #"Subject"
    body = db.Column(db.String(120)) #"Order"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)

    #You MUST initialize the fields of the class via init method
    def __init__(self, title, body, author, pub_date=None):
        self.title = title
        self.body = body
        self.author = author
        if pub_date is None:
            pub_date = datetime.now()
        self.pub_date = pub_date

#Use python shell to init database. from main (or model) import db, User, Order
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    store_num = db.Column(db.Integer, unique=True)
    orders = db.relationship('Order', backref='author')
    

    def __init__(self, email, password, store_num):
        self.email = email
        self.pw_hash = make_pw_hash(password)
        self.store_num = store_num
