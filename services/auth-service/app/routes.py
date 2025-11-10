from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, 
    create_refresh_token, get_jwt_identity,
    get_jwt
)
from .models import User, UserSession, RefreshToken, PasswordResetToken, db
from .security import validate_email, validate_password, generate_secure_token
from .utils import send_verification_email, send_password_reset_email
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Création du blueprint d'authentification
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé du service d'authentification
    """
    return jsonify({
        'status': 'healthy',
        'service': 'auth-service',
        'timestamp': datetime.utcnow().isoformat()
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Enregistrement d'un nouvel utilisateur
    
    Body JSON attendu:
        - email: Email de l'utilisateur
        - password: Mot de passe
        - first_name: Prénom
        - last_name: Nom
        - phone_number: Numéro de téléphone (optionnel)
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Champ obligatoire manquant: {field}',
                    'required_fields': required_fields
                }), 400
        
        # Validation de l'email
        if not validate_email(data['email']):
            return jsonify({'error': 'Format d\'email invalide'}), 400
        
        # Validation du mot de passe
        password_validation = validate_password(data['password'])
        if not password_validation['valid']:
            return jsonify({
                'error': 'Mot de passe invalide',
                'details': password_validation['errors']
            }), 400
        
        # Vérification si l'utilisateur existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Un utilisateur avec cet email existe déjà'}), 409
        
        # Création du nouvel utilisateur
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number')
        )
        user.set_password(data['password'])
        
        # Sauvegarde en base de données
        db.session.add(user)
        db.session.commit()
        
        # Envoi d'email de vérification (à implémenter)
        # send_verification_email(user)
        
        logger.info(f"Nouvel utilisateur enregistré: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de l'enregistrement: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion utilisateur
    
    Body JSON attendu:
        - email: Email de l'utilisateur
        - password: Mot de passe
    """
    try:
        data = request.get_json()
        
        # Validation des champs
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email et mot de passe requis'}), 400
        
        # Recherche de l'utilisateur
        user = User.query.filter_by(email=data['email']).first()
        
        # Vérification de l'utilisateur et du mot de passe
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Vérification si le compte est actif
        if not user.is_active:
            return jsonify({'error': 'Compte désactivé'}), 403
        
        # Mise à jour de la dernière connexion
        user.last_login = datetime.utcnow()
        
        # Création de la session utilisateur
        session = UserSession(
            user_id=user.id,
            device_info=request.headers.get('User-Agent', ''),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(session)
        db.session.commit()
        
        # Création des tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Sauvegarde du refresh token
        refresh_token_entry = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(refresh_token_entry)
        db.session.commit()
        
        logger.info(f"Utilisateur connecté: {user.email}")
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'session_id': session.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la connexion: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Rafraîchissement du token d'accès
    Requiert un refresh token valide
    """
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()["jti"]
        
        # Vérification du refresh token en base
        refresh_token = RefreshToken.query.filter_by(
            user_id=current_user_id, 
            token=jti,
            is_revoked=False
        ).first()
        
        if not refresh_token or refresh_token.is_expired():
            return jsonify({'error': 'Refresh token invalide ou expiré'}), 401
        
        # Création d'un nouveau token d'accès
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'access_token': new_access_token
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du rafraîchissement: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Déconnexion utilisateur
    Révoque le refresh token actuel
    """
    try:
        current_user_id = get_jwt_identity()
        jti = get_jwt()["jti"]
        
        # Révoquer le refresh token
        refresh_token = RefreshToken.query.filter_by(
            user_id=current_user_id,
            token=jti
        ).first()
        
        if refresh_token:
            refresh_token.is_revoked = True
            db.session.commit()
        
        # Marquer la session comme inactive
        current_session = UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).order_by(UserSession.login_at.desc()).first()
        
        if current_session:
            current_session.is_active = False
            current_session.logout_at = datetime.utcnow()
            db.session.commit()
        
        logger.info(f"Utilisateur déconnecté: {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Déconnexion réussie'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupération du profil utilisateur
    Requiert un token d'accès valide
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération profil: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/password/reset', methods=['POST'])
def request_password_reset():
    """
    Demande de réinitialisation de mot de passe
    """
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email requis'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        # Pour des raisons de sécurité, on ne révèle pas si l'email existe
        if user:
            # Génération du token de réinitialisation
            reset_token = generate_secure_token()
            
            reset_entry = PasswordResetToken(
                user_id=user.id,
                token=reset_token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            db.session.add(reset_entry)
            db.session.commit()
            
            # Envoi d'email (à implémenter)
            # send_password_reset_email(user, reset_token)
        
        return jsonify({
            'success': True,
            'message': 'Si l\'email existe, un lien de réinitialisation a été envoyé'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur demande réinitialisation: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

@auth_bp.route('/password/reset/confirm', methods=['POST'])
def confirm_password_reset():
    """
    Confirmation de réinitialisation de mot de passe
    """
    try:
        data = request.get_json()
        
        required_fields = ['token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        # Validation du token
        reset_token = PasswordResetToken.query.filter_by(
            token=data['token'],
            is_used=False
        ).first()
        
        if not reset_token or not reset_token.is_valid():
            return jsonify({'error': 'Token invalide ou expiré'}), 400
        
        # Validation du nouveau mot de passe
        password_validation = validate_password(data['new_password'])
        if not password_validation['valid']:
            return jsonify({
                'error': 'Mot de passe invalide',
                'details': password_validation['errors']
            }), 400
        
        # Mise à jour du mot de passe
        user = reset_token.user
        user.set_password(data['new_password'])
        
        # Marquer le token comme utilisé
        reset_token.is_used = True
        
        db.session.commit()
        
        logger.info(f"Mot de passe réinitialisé pour: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Mot de passe réinitialisé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur confirmation réinitialisation: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500