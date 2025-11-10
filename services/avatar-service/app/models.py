from datetime import datetime
import uuid
from typing import Dict, Any, Optional

class Avatar:
    """
    Modèle représentant un avatar numérique
    """
    
    def __init__(self, avatar_id: str, name: str, config: Dict[str, Any]):
        """
        Initialise un avatar
        
        Args:
            avatar_id: Identifiant unique de l'avatar
            name: Nom de l'avatar
            config: Configuration de l'avatar
        """
        self.avatar_id = avatar_id
        self.name = name
        self.config = config
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'avatar en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable de l'avatar
        """
        return {
            'avatar_id': self.avatar_id,
            'name': self.name,
            'config': self.config,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class AnimationSession:
    """
    Modèle représentant une session d'animation
    """
    
    def __init__(self, session_id: str, avatar_id: str, audio_data: bytes):
        """
        Initialise une session d'animation
        
        Args:
            session_id: Identifiant unique de la session
            avatar_id: ID de l'avatar à animer
            audio_data: Données audio pour la synchronisation
        """
        self.session_id = session_id
        self.avatar_id = avatar_id
        self.audio_data = audio_data
        self.created_at = datetime.utcnow()
        self.status = 'pending'  # pending, processing, completed, failed
        self.result_data: Optional[Dict[str, Any]] = None
        self.error_message: Optional[str] = None
    
    def update_status(self, status: str, result_data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """
        Met à jour le statut de la session
        
        Args:
            status: Nouveau statut
            result_data: Données du résultat (optionnel)
            error: Message d'erreur (optionnel)
        """
        self.status = status
        self.result_data = result_data
        self.error_message = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la session en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable de la session
        """
        return {
            'session_id': self.session_id,
            'avatar_id': self.avatar_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'result_data': self.result_data,
            'error_message': self.error_message
        }

class AvatarPreset:
    """
    Modèle représentant un preset d'avatar prédéfini
    """
    
    def __init__(self, preset_id: str, name: str, description: str, config: Dict[str, Any]):
        """
        Initialise un preset d'avatar
        
        Args:
            preset_id: Identifiant unique du preset
            name: Nom du preset
            description: Description du preset
            config: Configuration du preset
        """
        self.preset_id = preset_id
        self.name = name
        self.description = description
        self.config = config
        self.category = 'default'
        self.tags = []
        self.is_public = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le preset en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable du preset
        """
        return {
            'preset_id': self.preset_id,
            'name': self.name,
            'description': self.description,
            'config': self.config,
            'category': self.category,
            'tags': self.tags,
            'is_public': self.is_public
        }