from flask_restx import Resource
from flask import request
from database.db import get_db_connection
import hashlib
import secrets
import sqlite3
from functools import wraps

def generate_token():
    return secrets.token_hex(32)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
            result = cursor.fetchone()
            
            if not result:
                return {'message': 'Invalid token'}, 401
                
            return f(*args, **kwargs)
        finally:
            conn.close()
    return decorated

class Register(Resource):
    def __init__(self, *args):
        super().__init__()

    def post(self):
        try:
            data = request.get_json()
            print('Received data:', data)  # Debug print
            
            if not data:
                return {'message': 'No data received'}, 400
                
            username = data.get('username')
            password = data.get('password')
            
            print(f'Username: {username}, Password length: {len(password) if password else 0}')  # Debug print
            
            if not username or not password:
                return {'message': 'Missing username or password'}, 400
            
            hashed_password = hash_password(password)
            conn = get_db_connection()
            
            try:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                             (username, hashed_password))
                conn.commit()
                
                # Generate token for new user
                token = generate_token()
                cursor.execute('INSERT INTO tokens (user_id, token) VALUES (?, ?)',
                             (cursor.lastrowid, token))
                conn.commit()
                
                return {'message': 'User registered successfully', 'token': token}, 201
                
            except sqlite3.IntegrityError as e:
                print('Database error:', str(e))  # Debug print
                return {'message': 'Username already exists'}, 409
            except Exception as e:
                print('Unexpected error:', str(e))  # Debug print
                raise
            finally:
                conn.close()
        except Exception as e:
            print('Top-level error:', str(e))  # Debug print
            return {'message': 'An error occurred during registration', 'error': str(e)}, 500

class Login(Resource):
    def __init__(self, *args):
        super().__init__()

    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'message': 'Missing username or password'}, 400
        
        hashed_password = hash_password(password)
        conn = get_db_connection()
        
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?',
                         (username, hashed_password))
            user = cursor.fetchone()
            
            if not user:
                return {'message': 'Invalid credentials'}, 401
            
            # Generate new token
            token = generate_token()
            cursor.execute('INSERT INTO tokens (user_id, token) VALUES (?, ?)',
                         (user['id'], token))
            conn.commit()
            
            return {'message': 'Login successful', 'token': token}, 200
        finally:
            conn.close()

class Logout(Resource):
    def __init__(self, *args):
        super().__init__()

    @auth_required
    def post(self):
        token = request.headers.get('Authorization')
        conn = get_db_connection()
        
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tokens WHERE token = ?', (token,))
            conn.commit()
            return {'message': 'Logged out successfully'}, 200
        finally:
            conn.close()