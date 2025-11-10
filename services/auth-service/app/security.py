import re
import secrets
import string
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def validate_email(email):
    """
    Validation du format d'email
    
    Args:
        email: Adresse email à valider
        
    Returns:
        bool: True si l'email est valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validation de la force du mot de passe
    
    Args:
        password: Mot de passe à valider
        
    Returns:
        dict: Résultat de la validation avec détails
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if not any(char.isupper() for char in password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")
    
    if not any(char.islower() for char in password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")
    
    if not any(char.isdigit() for char in password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    if not any(char in string.punctuation for char in password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def generate_secure_token(length=32):
    """
    Génération d'un token sécurisé
    
    Args:
        length: Longueur du token (défaut: 32)
        
    Returns:
        str: Token sécurisé
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sanitize_input(input_string):
    """
    Nettoyage des entrées utilisateur pour prévenir les injections
    
    Args:
        input_string: Chaîne à nettoyer
        
    Returns:
        str: Chaîne nettoyée
    """
    if not input_string:
        return ""
    
    # Suppression des balises HTML/XML
    cleaned = re.sub(r'<[^>]*>', '', input_string)
    
    # Échappement des caractères spéciaux SQL
    cleaned = re.sub(r'[\'\";]', '', cleaned)
    
    # Limitation de la longueur
    return cleaned[:255]

def check_password_strength(password):
    """
    Évaluation de la force du mot de passe
    
    Args:
        password: Mot de passe à évaluer
        
    Returns:
        dict: Score et recommandations
    """
    score = 0
    feedback = []
    
    # Longueur
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Utilisez au moins 8 caractères")
    
    # Complexité
    checks = {
        'majuscule': any(c.isupper() for c in password),
        'minuscule': any(c.islower() for c in password),
        'chiffre': any(c.isdigit() for c in password),
        'spécial': any(c in string.punctuation for c in password)
    }
    
    score += sum(1 for check in checks.values() if check)
    
    for check_name, passed in checks.items():
        if not passed:
            feedback.append(f"Ajoutez des {check_name}")
    
    # Évaluation finale
    if score >= 5:
        strength = "Fort"
    elif score >= 3:
        strength = "Moyen"
    else:
        strength = "Faible"
    
    return {
        'score': score,
        'strength': strength,
        'feedback': feedback,
        'max_score': 6
    }

def validate_phone_number(phone):
    """
    Validation du numéro de téléphone
    
    Args:
        phone: Numéro de téléphone à valider
        
    Returns:
        bool: True si le numéro est valide
    """
    if not phone:
        return True  # Optionnel
    
    # Format international simple
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None