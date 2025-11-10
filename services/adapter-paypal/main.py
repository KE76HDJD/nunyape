from flask import Flask
from routes import paypal_bp
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """
    Factory function pour créer l'application Flask
    
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    
    # Enregistrement du blueprint avec préfixe d'URL
    app.register_blueprint(paypal_bp, url_prefix='/api/v1/paypal')
    
    @app.route('/')
    def root():
        """
        Endpoint racine avec informations du service
        """
        return {
            'service': 'paypal-adapter',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/v1/paypal/health',
                'create_payment': '/api/v1/paypal/payment/create',
                'execute_payment': '/api/v1/paypal/payment/execute'
            }
        }
    
    return app

if __name__ == '__main__':
    # Création et démarrage de l'application
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)