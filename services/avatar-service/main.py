from flask import Flask
from app.routes import avatar_bp
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """
    Application principale du service avatar
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SERVICE_NAME'] = 'avatar-service'
    app.config['VERSION'] = '1.0.0'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max pour les fichiers audio
    
    # Enregistrement des blueprints
    app.register_blueprint(avatar_bp, url_prefix='/api/v1/avatar')
    
    @app.route('/')
    def root():
        """
        Page racine avec documentation de l'API
        """
        return {
            'service': app.config['SERVICE_NAME'],
            'version': app.config['VERSION'],
            'endpoints': {
                'health': '/api/v1/avatar/health',
                'create_avatar': '/api/v1/avatar/avatar',
                'sync_animation': '/api/v1/avatar/animation/sync',
                'get_presets': '/api/v1/avatar/presets',
                'create_scene': '/api/v1/avatar/scene/create',
                'render': '/api/v1/avatar/render'
            },
            'description': 'Service de gestion d\'avatars et synchronisation labiale'
        }
    
    return app

if __name__ == '__main__':
    # Création et démarrage de l'application
    app = create_app()
    port = int(os.getenv('PORT', 8083))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Démarrage du service avatar sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)