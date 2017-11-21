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
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    orders = db.relationship('Order', backref='author')

    def __init__(self, email, password):
        self.email = email
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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        #If user exists, and their password matches what is in the database...
        if user and check_pw_hash(password, user.pw_hash):
            #'Remember' that the user has signed in
            session['email'] = email
            flash("Logged in")
            return redirect('/') #TODO change this to a more buyer friendly route

        elif user and user.password != password:
            flash('Password is incorrect')
            return redirect('/login')

        elif not user:
            flash('User does not exist')
            return redirect('/login')

    else:
        return render_template('login.html')


    return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if session:
        flash("You are already logged in")
        return redirect('/')

    if request.method == 'POST':
        #Grab the variables via request method
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #Set error checks
        email_error = '' #NOT USED BECAUSE OF 'EMAIL' TYPE IN HTML FORM
        password_error = ''
        verify_error = ''
        duplicate_user_error = ''

        # if not is_email(email): //COMMENTED OUT FOR NOW TO SEE IF THE ERROR STILL WORKS
        #     return redirect('/signup')
        
        if len(password) <= 3:
            password_error = "Your password is not long enough"
        elif len(password) >= 20:
            password_error ="Your password is too long"
        elif ' ' in password:
            password_error = "Your password cannot contain a space"
        
        if verify != password:
            verify_error = "Your passwords do not match"

        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            duplicate_user_error = "This user already exists"

        #Should no error occur...
        if not email_error and not password_error and not verify_error and not existing_user:
            new_user = User(email, password)
            db.session.add(new_user) #"stages" the new user for the db
            db.session.commit() #Actually adds the user to the db
            session['email'] = email
            flash('Signed in')
            return redirect('/')

        #If an error does occur...
        else:
            return render_template('signup.html',
            password_error = password_error,
            verify_error = verify_error,
            duplicate_user_error = duplicate_user_error)

    #If method == 'GET'     
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email'] 
    #flash('Logged out', 'no_error') This doesn't work, not sure why.
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')





if __name__ == "__main__":
    app.run()