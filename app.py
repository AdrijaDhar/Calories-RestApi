from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Entry, Role
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your models and routes below
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
