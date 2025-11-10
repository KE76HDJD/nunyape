from flask import Flask
from routes import stripe_bp
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(stripe_bp, url_prefix='/api/v1/stripe')
    
    @app.route('/')
    def root():
        return {
            'service': 'stripe-adapter',
            'version': '1.0.0',
            'status': 'running'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')