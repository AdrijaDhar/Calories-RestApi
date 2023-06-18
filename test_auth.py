import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User
from app import app
from app import db


class AuthTestCase(unittest.TestCase):
    
    
    def setUp(self):
        # Create the Flask test client
        self.app = app.test_client()

        # Establish an application context before running the tests
        self.app_context = app.app_context()
        self.app_context.push()

        # Create the database and tables
        db.create_all()

        
    def tearDown(self):
        # Remove the database and tables
        db.session.remove()
        db.drop_all()

        # Pop the application context after running the tests
        self.app_context.pop()


    def test_user_registration(self):
        with app.app_context():
            response = self.app.post('/register', data={'username': 'testuser', 'password': 'testpassword'})
            self.assertEqual(response.status_code, 201)


    def test_protected_route(self):
    # Create a test user in the database
        with app.app_context():
            user = User(username='testuser', password='password')
            db.session.add(user)
            db.session.commit()

        # Authenticate the user and obtain the access token
        # You can modify this code based on your authentication mechanism
        access_token = self.authenticate_user('testuser', 'password')

        # Set the authorization header with the access token
        headers = {'Authorization': f'Bearer {access_token}'}

        # Make a request to the protected route
        response = self.app.get('/protected', headers=headers)

        # Verify the response status code
        self.assertEqual(response.status_code, 200)

    # Add more assertions to verify the response content, headers, etc.

def test_user_login(self):
    # Create a test user in the database
    with app.app_context():
        user = User(username='testuser', password='password')
        db.session.add(user)
        db.session.commit()

    # Make a request to log in the user
    response = self.app.post('/login', data={'username': 'testuser', 'password': 'password'})

    # Verify the response status code
    self.assertEqual(response.status_code, 200)

    # Add more assertions to verify the response content, headers, etc.


if __name__ == '__main__':
    unittest.main()
