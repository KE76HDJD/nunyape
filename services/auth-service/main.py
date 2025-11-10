from app import create_auth_app
import os
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """
    Point d'entrée principal du service d'authentification
    """
    # Création de l'application
    app = create_auth_app()
    
    # Configuration du port et du mode debug
    port = int(os.getenv('PORT', 8081))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logging.info(f"Démarrage du service d'authentification sur le port {port}")
    
    # Démarrage de l'application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )

if __name__ == '__main__':
    main()