import logging
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

logger = logging.getLogger(__name__)

def generate_verification_token(email):
    """
    Génère un token de vérification d'email sécurisé
    
    Args:
        email: Email à vérifier
        
    Returns:
        str: Token de vérification
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_email_token(token, expiration=3600):
    """
    Vérifie un token de vérification d'email
    
    Args:
        token: Token à vérifier
        expiration: Temps d'expiration en secondes
        
    Returns:
        str: Email si valide, None sinon
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification',
            max_age=expiration
        )
        return email
    except Exception as e:
        logger.error(f"Erreur vérification token: {e}")
        return None

def send_verification_email(user):
    """
    Envoie un email de vérification (implémentation simulée)
    
    Args:
        user: Utilisateur à vérifier
    """
    try:
        token = generate_verification_token(user.email)
        verification_url = f"{current_app.config.get('FRONTEND_URL', '')}/verify-email?token={token}"
        
        # Log pour simulation - À remplacer par un vrai service d'email
        logger.info(f"Email de vérification pour {user.email}: {verification_url}")
        
        # Ici, on intégrerait un service comme SendGrid, Mailgun, etc.
        # email_service.send(
        #     to=user.email,
        #     subject="Vérification de votre email NUNYAPE",
        #     template="verification_email",
        #     context={'verification_url': verification_url}
        # )
        
    except Exception as e:
        logger.error(f"Erreur envoi email vérification: {e}")

def send_password_reset_email(user, reset_token):
    """
    Envoie un email de réinitialisation de mot de passe
    
    Args:
        user: Utilisateur concerné
        reset_token: Token de réinitialisation
    """
    try:
        reset_url = f"{current_app.config.get('FRONTEND_URL', '')}/reset-password?token={reset_token}"
        
        # Log pour simulation
        logger.info(f"Email réinitialisation mot de passe pour {user.email}: {reset_url}")
        
        # email_service.send(
        #     to=user.email,
        #     subject="Réinitialisation de votre mot de passe NUNYAPE",
        #     template="password_reset",
        #     context={'reset_url': reset_url}
        # )
        
    except Exception as e:
        logger.error(f"Erreur envoi email réinitialisation: {e}")

def format_error_message(error):
    """
    Formate les messages d'erreur pour l'API
    
    Args:
        error: Exception ou message d'erreur
        
    Returns:
        dict: Message d'erreur formaté
    """
    if hasattr(error, 'message'):
        message = error.message
    else:
        message = str(error)
    
    return {
        'error': message,
        'timestamp': datetime.utcnow().isoformat(),
        'success': False
    }

def log_user_activity(user_id, action, details=None):
    """
    Log une activité utilisateur pour l'audit
    
    Args:
        user_id: ID de l'utilisateur
        action: Action effectuée
        details: Détails supplémentaires
    """
    log_entry = {
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"Activité utilisateur: {log_entry}")

def calculate_token_expiry(hours=1):
    """
    Calcule la date d'expiration d'un token
    
    Args:
        hours: Heures avant expiration
        
    Returns:
        datetime: Date d'expiration
    """
    return datetime.utcnow() + timedelta(hours=hours)