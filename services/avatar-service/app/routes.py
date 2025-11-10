from flask import Blueprint, request, jsonify, current_app
import logging
import uuid
from datetime import datetime
from .lipsync import LipSyncEngine
from .models import Avatar, AnimationSession, AvatarPreset
from .scene_manager import SceneManager

logger = logging.getLogger(__name__)

# Initialisation des composants
lip_sync_engine = LipSyncEngine()
scene_manager = SceneManager()

# Création du blueprint
avatar_bp = Blueprint('avatar', __name__)

# Stockage en mémoire (à remplacer par une base de données)
avatars_store = {}
sessions_store = {}
presets_store = {}

@avatar_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé du service avatar
    """
    return jsonify({
        'status': 'healthy',
        'service': 'avatar-service',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'lip_sync': 'active',
            'scene_manager': 'active'
        }
    })

@avatar_bp.route('/avatar', methods=['POST'])
def create_avatar():
    """
    Crée un nouvel avatar
    
    Body JSON attendu:
        - name: Nom de l'avatar
        - config: Configuration de l'avatar
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        if not data.get('name'):
            return jsonify({'error': 'Le nom de l\'avatar est obligatoire'}), 400
        
        # Génération d'un ID unique
        avatar_id = str(uuid.uuid4())
        
        # Configuration par défaut
        default_config = {
            'type': 'default',
            'resolution': '1024x1024',
            'format': 'mp4',
            'fps': 30
        }
        
        # Fusion avec la configuration fournie
        avatar_config = {**default_config, **data.get('config', {})}
        
        # Création de l'avatar
        avatar = Avatar(avatar_id, data['name'], avatar_config)
        avatars_store[avatar_id] = avatar
        
        logger.info(f"Avatar créé: {avatar_id} - {data['name']}")
        
        return jsonify({
            'success': True,
            'avatar': avatar.to_dict(),
            'message': 'Avatar créé avec succès'
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur création avatar: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/avatar/<avatar_id>', methods=['GET'])
def get_avatar(avatar_id):
    """
    Récupère les informations d'un avatar
    
    Args:
        avatar_id: ID de l'avatar
    """
    try:
        avatar = avatars_store.get(avatar_id)
        
        if not avatar:
            return jsonify({'error': 'Avatar non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'avatar': avatar.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération avatar: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/animation/sync', methods=['POST'])
def sync_animation():
    """
    Synchronise l'animation d'un avatar avec un audio
    
    Body JSON attendu:
        - avatar_id: ID de l'avatar
        - audio_data: Données audio encodées en base64
        - config: Configuration optionnelle de l'animation
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['avatar_id', 'audio_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400
        
        # Vérification de l'existence de l'avatar
        avatar = avatars_store.get(data['avatar_id'])
        if not avatar:
            return jsonify({'error': 'Avatar non trouvé'}), 404
        
        # Génération d'un ID de session
        session_id = str(uuid.uuid4())
        
        # Création de la session
        session = AnimationSession(session_id, data['avatar_id'], data['audio_data'])
        sessions_store[session_id] = session
        
        # Traitement de la synchronisation labiale
        audio_data = data['audio_data']  # En base64 dans un cas réel
        
        # Analyse audio
        phoneme_data = lip_sync_engine.analyze_audio(audio_data.encode() if isinstance(audio_data, str) else audio_data)
        
        if not phoneme_data['success']:
            session.update_status('failed', error=phoneme_data.get('error'))
            return jsonify({'error': 'Échec de l\'analyse audio'}), 500
        
        # Génération des visèmes
        viseme_data = lip_sync_engine.generate_viseme_sequence(phoneme_data)
        
        if not viseme_data['success']:
            session.update_status('failed', error=viseme_data.get('error'))
            return jsonify({'error': 'Échec de la génération des visèmes'}), 500
        
        # Synchronisation avec l'avatar
        animation_data = lip_sync_engine.synchronize_with_avatar(viseme_data, avatar.config)
        
        if not animation_data['success']:
            session.update_status('failed', error=animation_data.get('error'))
            return jsonify({'error': 'Échec de la synchronisation'}), 500
        
        # Mise à jour de la session avec le résultat
        session.update_status('completed', result_data=animation_data)
        
        logger.info(f"Animation synchronisée: {session_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'animation_data': animation_data,
            'message': 'Animation synchronisée avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur synchronisation animation: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/animation/session/<session_id>', methods=['GET'])
def get_animation_session(session_id):
    """
    Récupère le statut d'une session d'animation
    
    Args:
        session_id: ID de la session
    """
    try:
        session = sessions_store.get(session_id)
        
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération session: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/presets', methods=['GET'])
def get_avatar_presets():
    """
    Récupère la liste des presets d'avatar disponibles
    """
    try:
        # Génération de quelques presets par défaut
        if not presets_store:
            default_presets = [
                AvatarPreset(
                    preset_id=str(uuid.uuid4()),
                    name='Avatar Standard',
                    description='Avatar par défaut avec configuration standard',
                    config={
                        'type': 'standard',
                        'resolution': '1024x1024',
                        'format': 'mp4',
                        'fps': 30
                    }
                ),
                AvatarPreset(
                    preset_id=str(uuid.uuid4()),
                    name='Avatar HD',
                    description='Avatar haute définition',
                    config={
                        'type': 'hd',
                        'resolution': '2048x2048',
                        'format': 'mp4',
                        'fps': 60
                    }
                ),
                AvatarPreset(
                    preset_id=str(uuid.uuid4()),
                    name='Avatar Unity',
                    description='Avatar optimisé pour Unity',
                    config={
                        'type': 'unity',
                        'resolution': '1024x1024',
                        'format': 'fbx',
                        'fps': 30
                    }
                )
            ]
            
            for preset in default_presets:
                presets_store[preset.preset_id] = preset
        
        presets_list = [preset.to_dict() for preset in presets_store.values()]
        
        return jsonify({
            'success': True,
            'presets': presets_list,
            'count': len(presets_list)
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération presets: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/scene/create', methods=['POST'])
def create_scene():
    """
    Crée une nouvelle scène pour l'avatar
    
    Body JSON attendu:
        - avatar_id: ID de l'avatar
        - scene_config: Configuration de la scène
    """
    try:
        data = request.get_json()
        
        if not data.get('avatar_id'):
            return jsonify({'error': 'avatar_id est obligatoire'}), 400
        
        avatar = avatars_store.get(data['avatar_id'])
        if not avatar:
            return jsonify({'error': 'Avatar non trouvé'}), 404
        
        scene_config = data.get('scene_config', {})
        scene_data = scene_manager.create_scene(avatar, scene_config)
        
        return jsonify({
            'success': True,
            'scene': scene_data,
            'message': 'Scène créée avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur création scène: {e}")
        return jsonify({'error': str(e)}), 500

@avatar_bp.route('/render', methods=['POST'])
def render_animation():
    """
    Lance le rendu d'une animation
    
    Body JSON attendu:
        - session_id: ID de la session d'animation
        - render_config: Configuration du rendu
    """
    try:
        data = request.get_json()
        
        if not data.get('session_id'):
            return jsonify({'error': 'session_id est obligatoire'}), 400
        
        session = sessions_store.get(data['session_id'])
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404
        
        if session.status != 'completed':
            return jsonify({'error': 'Session non terminée'}), 400
        
        render_config = data.get('render_config', {})
        render_result = scene_manager.render_animation(session, render_config)
        
        return jsonify({
            'success': True,
            'render_result': render_result,
            'message': 'Rendu lancé avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur rendu animation: {e}")
        return jsonify({'error': str(e)}), 500