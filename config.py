from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SECRET_KEY'] = 'your_secret_key'

# database initialization
db = SQLAlchemy(app)