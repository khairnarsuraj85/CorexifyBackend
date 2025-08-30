from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime
from functools import wraps
import bcrypt
from app.models import AdminUser

auth = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            admin_id = data['admin_id']
            
            # Fetch user from Firestore database
            current_admin = AdminUser.get_by_id(admin_id)

            if not current_admin:
                return jsonify({'error': 'Invalid token user'}), 401

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'error': 'Token is invalid or expired'}), 401
        except Exception as e:
            return jsonify({'error': 'Unexpected error', 'details': str(e)}), 500

        return f(current_admin, *args, **kwargs)

    return decorated


@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password are required"}), 400

        email = data['email'].lower()
        password = data['password']

        # Fetch admin from Firestore
        admin = AdminUser.get_by_email(email)

        if not admin or not bcrypt.checkpw(password.encode('utf-8'), admin['password_hash'].encode('utf-8')):
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate JWT token
        token = jwt.encode({
            'admin_id': admin['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['JWT_SECRET'], algorithm='HS256')

        # Don't send the password hash to the client
        admin.pop('password_hash', None)
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "admin": admin,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/register', methods=['POST'])
@token_required
def register(current_admin):
    try:
        # ✅ CORRECTED: Only super admins can create other admins.
        # This checks the boolean flag from the database instead of a hardcoded email.
        if not current_admin.get('is_super_admin', False):
            return jsonify({"error": "Authorization failed: Only super admins can create new admin users"}), 403

        data = request.get_json()
        required_fields = ['email', 'password', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Email, password, and name are required"}), 400

        email = data['email'].lower()
        
        if AdminUser.get_by_email(email):
            return jsonify({"error": "Admin with this email already exists"}), 409

        # Hash the password
        password = data['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        
        new_admin_data = {
            "email": email,
            "password_hash": hashed_password,
            "name": data.get('name', ''),
            "is_super_admin": data.get('is_super_admin', False)
        }

        new_admin_id = AdminUser.create(new_admin_data)

        return jsonify({
            "message": "Admin user created successfully",
            "admin_id": new_admin_id,
            "status": "success"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
