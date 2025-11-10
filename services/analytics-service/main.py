from flask import Flask
from routes import analytics_bp
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """
    Factory function pour créer l'application Flask du service analytique
    """
    app = Flask(__name__)
    
    # Enregistrement du blueprint
    app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
    
    @app.route('/')
    def root():
        """
        Endpoint racine avec documentation des API
        """
        return {
            'service': 'analytics-service',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/v1/analytics/health',
                'full_report': '/api/v1/analytics/report',
                'revenue_metrics': '/api/v1/analytics/metrics/revenue',
                'health_status': '/api/v1/analytics/health/status',
                'transactions_summary': '/api/v1/analytics/transactions/summary'
            }
        }
    
    return app

if __name__ == '__main__':
    # Création et démarrage de l'application
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)