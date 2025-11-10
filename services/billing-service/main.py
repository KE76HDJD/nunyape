from flask import Flask
from app.routes import billing_bp
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """
    Application principale du service de facturation
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SERVICE_NAME'] = 'billing-service'
    app.config['VERSION'] = '1.0.0'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
    
    # Enregistrement des blueprints
    app.register_blueprint(billing_bp, url_prefix='/api/v1/billing')
    
    @app.route('/')
    def root():
        """
        Page racine avec documentation de l'API
        """
        return {
            'service': app.config['SERVICE_NAME'],
            'version': app.config['VERSION'],
            'endpoints': {
                'health': '/api/v1/billing/health',
                'create_customer': '/api/v1/billing/customers',
                'create_invoice': '/api/v1/billing/invoices',
                'get_invoice_pdf': '/api/v1/billing/invoices/{id}/pdf',
                'record_payment': '/api/v1/billing/invoices/{id}/pay',
                'create_subscription': '/api/v1/billing/subscriptions',
                'send_reminders': '/api/v1/billing/notifications/reminders',
                'revenue_report': '/api/v1/billing/reports/revenue'
            },
            'description': 'Service de facturation et gestion des paiements NUNYAPE'
        }
    
    return app

if __name__ == '__main__':
    # Création et démarrage de l'application
    app = create_app()
    port = int(os.getenv('PORT', 8084))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Démarrage du service de facturation sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)