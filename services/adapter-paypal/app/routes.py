from flask import Blueprint, request, jsonify
from paypal_client import PayPalClient
import os
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Configuration des variables d'environnement
PAYPAL_BASE_URL = os.getenv('PAYPAL_BASE_URL', 'https://api.sandbox.paypal.com')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

# Initialisation du client PayPal
paypal_client = PayPalClient(PAYPAL_BASE_URL, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)

# Création du blueprint Flask
paypal_bp = Blueprint('paypal', __name__)

@paypal_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel
    
    Returns:
        Statut de santé du service
    """
    return jsonify({
        'status': 'healthy', 
        'service': 'paypal-adapter',
        'timestamp': '2025-01-27T21:27:26Z'
    })

@paypal_bp.route('/payment/create', methods=['POST'])
def create_payment():
    """
    Crée un nouveau paiement PayPal
    
    Body JSON attendu:
        - amount: Montant du paiement
        - currency: Devise (EUR, USD, etc.)
        - return_url: URL de retour après succès
        - cancel_url: URL d'annulation
    
    Returns:
        Données de création du paiement avec URL d'approbation
    """
    try:
        # Récupération des données de la requête
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['amount', 'currency', 'return_url', 'cancel_url']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Champ obligatoire manquant: {field}',
                    'required_fields': required_fields
                }), 400
        
        # Création du paiement via le client PayPal
        payment = paypal_client.create_payment(
            amount=data['amount'],
            currency=data['currency'],
            return_url=data['return_url'],
            cancel_url=data['cancel_url']
        )
        
        # Extraction de l'URL d'approbation
        approval_url = next(
            (link['href'] for link in payment['links'] if link['rel'] == 'approval_url'),
            None
        )
        
        return jsonify({
            'success': True,
            'payment_id': payment['id'],
            'status': payment['state'],
            'approval_url': approval_url,
            'adapter': 'paypal'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du paiement: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@paypal_bp.route('/payment/execute', methods=['POST'])
def execute_payment():
    """
    Exécute un paiement PayPal après approbation utilisateur
    
    Body JSON attendu:
        - payment_id: ID du paiement à exécuter
        - payer_id: ID du payeur (retourné par PayPal après approbation)
    
    Returns:
        Statut d'exécution du paiement
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['payment_id', 'payer_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Champ obligatoire manquant: {field}',
                    'required_fields': required_fields
                }), 400
        
        # Exécution du paiement
        result = paypal_client.execute_payment(
            payment_id=data['payment_id'],
            payer_id=data['payer_id']
        )
        
        return jsonify({
            'success': True,
            'transaction_id': result.get('id'),
            'status': result.get('state'),
            'adapter': 'paypal'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du paiement: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@paypal_bp.route('/payment/<payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    Récupère les détails d'un paiement spécifique
    
    Args:
        payment_id: ID du paiement à consulter
    
    Returns:
        Détails complets du paiement
    """
    try:
        payment_details = paypal_client.get_payment_details(payment_id)
        
        return jsonify({
            'success': True,
            'payment': payment_details,
            'adapter': 'paypal'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du paiement: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500