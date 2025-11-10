from flask import Blueprint, request, jsonify
from stripe_client import StripeClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')

# Initialisation du client Stripe
stripe_client = StripeClient(STRIPE_API_KEY)

# Création du blueprint
stripe_bp = Blueprint('stripe', __name__)

@stripe_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour Stripe
    """
    return jsonify({'status': 'healthy', 'adapter': 'stripe'})

@stripe_bp.route('/payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Crée un Payment Intent Stripe
    """
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'currency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        payment_intent = stripe_client.create_payment_intent(
            amount=data['amount'],
            currency=data['currency'],
            customer_id=data.get('customer_id')
        )
        
        return jsonify({
            'success': True,
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'status': payment_intent.status,
            'adapter': 'stripe'
        })
        
    except Exception as e:
        logger.error(f"Erreur création Payment Intent: {e}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/payment-intent/<payment_intent_id>/confirm', methods=['POST'])
def confirm_payment(payment_intent_id):
    """
    Confirme un paiement Stripe
    """
    try:
        data = request.get_json()
        
        if 'payment_method' not in data:
            return jsonify({'error': 'Champ payment_method manquant'}), 400
        
        payment_intent = stripe_client.confirm_payment(
            payment_intent_id=payment_intent_id,
            payment_method=data['payment_method']
        )
        
        return jsonify({
            'success': True,
            'payment_intent_id': payment_intent.id,
            'status': payment_intent.status,
            'adapter': 'stripe'
        })
        
    except Exception as e:
        logger.error(f"Erreur confirmation paiement: {e}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/customer', methods=['POST'])
def create_customer():
    """
    Crée un client Stripe
    """
    try:
        data = request.get_json()
        
        required_fields = ['email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        customer = stripe_client.create_customer(
            email=data['email'],
            name=data['name']
        )
        
        return jsonify({
            'success': True,
            'customer_id': customer.id,
            'adapter': 'stripe'
        })
        
    except Exception as e:
        logger.error(f"Erreur création client: {e}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/refund', methods=['POST'])
def create_refund():
    """
    Crée un remboursement Stripe
    """
    try:
        data = request.get_json()
        
        if 'payment_intent_id' not in data:
            return jsonify({'error': 'Champ payment_intent_id manquant'}), 400
        
        refund = stripe_client.create_refund(
            payment_intent_id=data['payment_intent_id'],
            amount=data.get('amount')
        )
        
        return jsonify({
            'success': True,
            'refund_id': refund.id,
            'status': refund.status,
            'adapter': 'stripe'
        })
        
    except Exception as e:
        logger.error(f"Erreur création remboursement: {e}")
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/payment-intent/<payment_intent_id>', methods=['GET'])
def get_payment_intent(payment_intent_id):
    """
    Récupère un Payment Intent
    """
    try:
        payment_intent = stripe_client.get_payment_intent(payment_intent_id)
        
        return jsonify({
            'success': True,
            'payment_intent': {
                'id': payment_intent.id,
                'status': payment_intent.status,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency
            },
            'adapter': 'stripe'
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération Payment Intent: {e}")
        return jsonify({'error': str(e)}), 500