import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User
from app import app
from app import db


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.app = app.test_client()  # Create a test client for making requests

        with app.app_context():
            db.create_all()
    
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


    def test_user_registration(self):
        with app.app_context():
            response = self.app.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
            self.assertEqual(response.status_code, 201)


    def test_user_login(self):
        # Register a test user
        self.app.post('/register', data={'username': 'testuser', 'password': 'testpassword'})

        # Test login with correct credentials
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully', response.data)

        # Test login with incorrect credentials
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid username or password', response.data)

    def test_protected_route(self):
        # Access a protected route without authentication
        response = self.app.get('/entries')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Missing Authorization Header', response.data)

        # Register a test user
        self.app.post('/register', data={'username': 'testuser', 'password': 'testpassword'})

        # Login to get the access token
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        token = response.json['access_token']

        # Access the protected route with authentication
        response = self.app.get('/entries', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        # Add assertions for the expected response data

if __name__ == '__main__':
    unittest.main()
