from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from isemail import is_email
from hashutils import make_pw_hash, check_pw_hash



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://koerner-dev:koerner@localhost:3306/koerner-dev'
app.config['SQLALCHEMY_ECHO'] = True
#The database
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

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
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

#Use python shell to init database. from main import db, User, Order
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)






#Filter ALL incoming requests here:


# @app.before_request
# def requre_login():
#     allowed_routes = ['login', 'signup'] #ADD MORE
#     if request.endpoint not in allowed_routes:
#         #TODO: flash a message
#         return render_template('oldenough.html')
#     return render_template('base.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():

    return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        #Grab the variables via request method
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #Set error checks
        email_error = ''
        password_error = ''
        verify_error = ''
        duplicate_user_error = ''

        if not is_email(email):
            return redirect('/signup')
        TODO:"START HERE"

    
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')





if __name__ == "__main__":
    app.run()