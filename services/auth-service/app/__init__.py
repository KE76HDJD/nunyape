"""
Package d'authentification NUNYAPE
Gère l'authentification, l'autorisation et la sécurité des utilisateurs
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

# Initialisation des extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_auth_app():
    """
    Factory pour créer l'application d'authentification
    
    Returns:
        Application Flask configurée pour l'authentification
    """
    app = Flask(__name__)
    
    # Configuration de base
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///auth_service.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 heure
    
    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Import et enregistrement des blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    
    # Création des tables de base de données
    with app.app_context():
        db.create_all()
    
    return app