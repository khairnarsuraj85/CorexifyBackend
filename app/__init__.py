from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import cloudinary

# Load environment variables from the .env file in the root directory
load_dotenv()

def create_app():
    """
    Application factory function. Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # --- Core Application Configuration ---
    # Load secret keys from environment variables. Crucial for security.
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    
    # --- Super Admin Configuration ---
    # Defines the primary super administrator for the application
    app.config['SUPER_ADMIN_EMAIL'] = os.getenv('SUPER_ADMIN_EMAIL')

    # --- SMTP Configuration for Sending Emails ---
    app.config['ADMIN_EMAIL'] = os.getenv('ADMIN_EMAIL')
    app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
    app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    app.config['SMTP_PORT'] = int(os.getenv('SMTP_PORT', 587))

    # --- Cloudinary Configuration ---
    # Initializes the Cloudinary library with credentials from the .env file.
    # This allows the application to upload and manage media files.
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET'),
        secure=True # Ensures all URLs are generated with HTTPS
    )
    
    # --- CORS (Cross-Origin Resource Sharing) Configuration ---
    # Allows your React frontend to make requests to this Flask backend.
    origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://68b3dc3d92f982a7c71b312c--teamcorexify.netlify.app"  # Add your Netlify URL here
    ]

    frontend_url = os.getenv('FRONTEND_URL')
    if frontend_url:
        origins.append(frontend_url)

    CORS(app, origins=origins, supports_credentials=True)

    # --- Register Blueprints (Route Groups) ---
    # Import and register the different parts of your application.
    from app.routes import main as main_blueprint
    from app.auth import auth as auth_blueprint
    from app.admin_routes import admin_bp as admin_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app
