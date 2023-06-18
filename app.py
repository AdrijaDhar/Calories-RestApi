from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User, Entry, Role
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your models and routes below
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
    
    
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    role_id = data['role_id']  # Assuming you have predefined role IDs (e.g., 1 for regular user, 2 for user manager, 3 for admin)

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify(message='Username already exists'), 400

    password_hash = generate_password_hash(password)

    new_user = User(username=username, password_hash=password_hash, role_id=role_id)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User registered successfully'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify(message='Invalid username or password'), 401

    # Generate a JWT token for authentication
    token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'])

    return jsonify(token=token.decode('utf-8')), 200

