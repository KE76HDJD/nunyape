from flask import Flask
from routes import flooz_bp
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    app = Flask(__name__)
    
    # Register blueprint
    app.register_blueprint(flooz_bp, url_prefix='/api/v1/flooz')
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'service': 'flooz-adapter',
            'version': '1.0.0',
            'status': 'running'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')