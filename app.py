from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://koerner-dev:koerner@localhost:3306/koerner-dev'
app.config['SQLALCHEMY_ECHO'] = True
#The database
db = SQLAlchemy(app)