from flask import Blueprint, request, jsonify
from flooz_client import FloozClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
FLOOZ_BASE_URL = os.getenv('FLOOZ_BASE_URL', 'https://api.flooz.com/v1')
FLOOZ_API_KEY = os.getenv('FLOOZ_API_KEY')

# Initialize client
flooz_client = FloozClient(FLOOZ_BASE_URL, FLOOZ_API_KEY)

# Create Blueprint
flooz_bp = Blueprint('flooz', __name__)

@flooz_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'adapter': 'flooz'})

@flooz_bp.route('/payment', methods=['POST'])
def process_payment():
    """Process payment through Flooz"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'recipient', 'reference']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process payment
        result = flooz_client.process_payment(
            amount=data['amount'],
            recipient=data['recipient'],
            reference=data['reference']
        )
        
        return jsonify({
            'success': True,
            'transaction_id': result.get('transaction_id'),
            'status': result.get('status'),
            'adapter': 'flooz'
        })
        
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return jsonify({'error': str(e)}), 500

@flooz_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get account balance"""
    try:
        balance = flooz_client.check_balance()
        return jsonify({
            'success': True,
            'balance': balance,
            'adapter': 'flooz'
        })
    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return jsonify({'error': str(e)}), 500

@flooz_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction status"""
    try:
        transaction = flooz_client.get_transaction_status(transaction_id)
        return jsonify({
            'success': True,
            'transaction': transaction,
            'adapter': 'flooz'
        })
    except Exception as e:
        logger.error(f"Transaction status error: {e}")
        return jsonify({'error': str(e)}), 500