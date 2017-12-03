from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import date
from sqlalchemy import desc
from isemail import is_email
from hashutils import make_pw_hash, check_pw_hash

#LOOK UP STRIPE LIBRARY################################################

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
            pub_date = datetime.now()
        self.pub_date = pub_date

#Use python shell to init database. from main import db, User, Order
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






#Filter ALL incoming requests here:


# @app.before_request
# def requre_login():
#     allowed_routes = ['login', 'signup'] #ADD MORE
#     if request.endpoint not in allowed_routes:
#         #TODO: flash a message
#         return render_template('oldenough.html')
#     return render_template('base.html')

@app.route('/oldenough')
def oldenough():
    return render_template('oldenough.html')

@app.route('/login', methods=['GET'])
def displaylogin():
    return render_template("login.html")

@app.route('/login', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()

        #If user exists, and their password matches what is in the database...
    if user and check_pw_hash(password, user.pw_hash):
        #'Remember' that the user has signed in
        session['email'] = email
        flash("Logged in", "success")
        return redirect('/')

    elif user and user.pw_hash != password:
        flash('Password is incorrect', "error")
        return redirect('/login')

    elif not is_email(email):
        flash("Invalid email", "error")
        return redirect('/login')

    elif not user:
        flash('User does not exist', "error")
        return redirect('/login')


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
        store_num = request.form['store_num']

        #Set error checks
        email_error = '' #NOT USED BECAUSE OF 'EMAIL' TYPE IN HTML FORM
        password_error = ''
        verify_error = ''
        store_num_error = ''
        duplicate_user_error = ''

        if not is_email(email):
            email_error = "Not a valid email"
        
        if len(password) <= 3:
            password_error = "Your password is not long enough"
        elif len(password) >= 20:
            password_error ="Your password is too long"
        elif ' ' in password:
            password_error = "Your password cannot contain a space"
        
        if verify != password:
            verify_error = "Your passwords do not match"

        if len(store_num) != 5:
            store_num_error = "Invalid store number"

        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            duplicate_user_error = "This user already exists"

        #Should no error occur...
        if not email_error and not password_error and not verify_error and not existing_user and not store_num_error:
            new_user = User(email, password, store_num)
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
            duplicate_user_error = duplicate_user_error,
            store_num_error = store_num_error)

    #If method == 'GET'     
    return render_template('signup.html')

@app.route('/order', methods=["GET"])
def showOrder():
    #If somehow the user clicks this without signing in...
    if len(session)==0:
        flash("You need to log in to do that")
        return redirect('/login')

    #Check for query params...
    order_id = request.args.get('id')
        
    #If there is an id...
    #Bring the buyer to his display order page...
    if order_id:
        order = Order.query.get(order_id)
        buyers = User.query.all()
        return render_template('displayorder.html', order=order, buyers=buyers)

    #If there is no id present, render the regular order page:
    else:
        return render_template('order.html')

@app.route('/order', methods=["POST"])
def placeOrder():
        #Grab specific buyer that this order will be linked to...
        buyer = User.query.filter_by(email=session['email']).first()

        #Use request form to grab the form 
        order_title = request.form['subject']
        order_body = request.form['order']

        title_error = ""
        body_error = ""

        if len(order_title) == 0:
            title_error = "Your order needs a title"
        if len(order_body) < 5:
            body_error = "We cannot help you if you do not describe the order in detail, try again"
        
        #If there is no error...
        if not title_error and not body_error:

            new_order = Order(order_title, order_body, buyer)
            db.session.add(new_order)
            db.session.commit()

            return redirect('/order?id={}'.format(new_order.id))

        else:
            return render_template('order.html',
            title_error=title_error,
            body_error=body_error,
            order_body=order_body)


@app.route("/buyerhistory", methods = ["GET"])
def buyerHistory():
    #We need to grab the buyer whos info we need to gather, we do this via the session
    #We then grab all the order to loop through until we match the ids
    buyer = User.query.filter_by(email=session['email']).first()
    all_orders = Order.query.order_by(desc(Order.pub_date)).all()

    #In order to display the orders in the correct order (descending), summon all the orders and add
    #the ones whos user_id attribute (a foreign key) is equal to the buyer.id that we got earlier
    buyer_orders = []

    for order in all_orders:
        if order.user_id == buyer.id:
            buyer_orders.append(order)
     
    
    return render_template("buyerhistory.html", buyer=buyer, orders=buyer_orders) 

@app.route("/offices", methods=["GET"])
def displayOffices():
    return render_template("offices.html")


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