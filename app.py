from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import requests
from flask_login import LoginManager
from datetime import datetime
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask import Blueprint
from models import User
auth = Blueprint('auth', __name__)



app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    text = db.Column(db.String(256), nullable=False)
    calories = db.Column(db.Integer)
    is_below_expected = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def protected_route(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            jwt_required()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if not current_user:
                raise Exception('Invalid user')
        except Exception as e:
            return jsonify(message='Authentication required'), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    role_id = data['role_id']

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

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


@app.route('/entries', methods=['POST'])
@protected_route
def create_entry(current_user):
    data = request.get_json()
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    time = data['time']
    text = data['text']
    calories = data.get('calories')

    if calories is None:
        # to retrieve calories from a Calories API provider
        # Updating the 'calories' variable with the retrieved value
         request_data = {
        'meal_text': text
    }

    # Making a POST request to the Calories API provider
    response = requests.post('https://www.nutritionix.com/api/calories', json=request_data)

    if response.status_code == 200:
        # Retrieving the calories from the response
        calories_data = response.json()
        calories = calories_data.get('calories')

        # Updating the 'calories' variable with the retrieved value
        if calories is not None:
            new_entry.calories = calories
        pass

    # Determining if the entry is below expected calories
    total_calories = Entry.query.filter_by(user_id=current_user.id, date=date).with_entities(db.func.sum(Entry.calories)).scalar()
    if total_calories is not None and current_user.expected_calories is not None:
        is_below_expected = total_calories < current_user.expected_calories
    else:
        is_below_expected = False

    new_entry = Entry(date=date, time=time, text=text, calories=calories, user_id=current_user.id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify(message='Entry created successfully'), 201


@app.route('/entries', methods=['GET'])
@protected_route
def get_entries(current_user):
    entries = Entry.query.filter_by(user_id=current_user.id).all()
    entries_data = [{'id': entry.id, 'date': entry.date, 'time': entry.time, 'text': entry.text, 'calories': entry.calories} for entry in entries]

    return jsonify(entries=entries_data), 200


@app.route('/entries/<int:entry_id>', methods=['PUT'])
@protected_route
def update_entry(current_user, entry_id):
    entry = Entry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        return jsonify(message='Entry not found'), 404

    data = request.get_json()
    text = data['text']
    calories = data.get('calories')

    entry.text = text
    entry.calories = calories

    # Determine if the entry is below expected calories
    total_calories = Entry.query.filter_by(user_id=current_user.id, date=entry.date).with_entities(db.func.sum(Entry.calories)).scalar()
    if total_calories is not None and current_user.expected_calories is not None:
        entry.is_below_expected = total_calories < current_user.expected_calories
    else:
        entry.is_below_expected = False


    db.session.commit()

    return jsonify(message='Entry updated successfully'), 200


@app.route('/entries/<int:entry_id>', methods=['DELETE'])
@protected_route
def delete_entry(current_user, entry_id):
    entry = Entry.query.filter_by(id=entry_id, user_id=current_user.id).first()
    if not entry:
        return jsonify(message='Entry not found'), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify(message='Entry deleted successfully'), 200

def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth)
if __name__ == '__main__':
    app.run(debug=True)
