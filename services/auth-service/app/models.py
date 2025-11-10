from . import db, bcrypt
from datetime import datetime, timedelta
import uuid

class User(db.Model):
    """
    Modèle utilisateur pour l'authentification
    Gère les informations de compte et la sécurité
    """
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    sessions = db.relationship('UserSession', backref='user', lazy=True)
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True)
    
    def set_password(self, password):
        """
        Hash et définit le mot de passe utilisateur
        
        Args:
            password: Mot de passe en clair
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """
        Vérifie le mot de passe utilisateur
        
        Args:
            password: Mot de passe en clair à vérifier
            
        Returns:
            bool: True si le mot de passe correspond
        """
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """
        Convertit l'utilisateur en dictionnaire (sans informations sensibles)
        
        Returns:
            dict: Représentation sécurisée de l'utilisateur
        """
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class UserSession(db.Model):
    """
    Modèle de session utilisateur
    Track les sessions actives pour la sécurité
    """
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    device_info = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    login_at = db.Column(db.DateTime, default=datetime.utcnow)
    logout_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """
        Convertit la session en dictionnaire
        
        Returns:
            dict: Représentation de la session
        """
        return {
            'id': self.id,
            'device_info': self.device_info,
            'ip_address': self.ip_address,
            'login_at': self.login_at.isoformat(),
            'is_active': self.is_active
        }

class RefreshToken(db.Model):
    """
    Modèle pour les tokens de rafraîchissement JWT
    Permet de renouveler les tokens d'accès
    """
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_expired(self):
        """
        Vérifie si le token a expiré
        
        Returns:
            bool: True si expiré
        """
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """
        Vérifie si le token est valide (non révoqué et non expiré)
        
        Returns:
            bool: True si valide
        """
        return not self.is_revoked and not self.is_expired()

class PasswordResetToken(db.Model):
    """
    Modèle pour les tokens de réinitialisation de mot de passe
    """
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """
        Vérifie si le token de réinitialisation est valide
        
        Returns:
            bool: True si valide
        """
        return not self.is_used and datetime.utcnow() <= self.expires_at