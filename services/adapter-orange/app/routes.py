from flask import Blueprint, request, jsonify
from orange_client import OrangeClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
ORANGE_BASE_URL = os.getenv('ORANGE_BASE_URL', 'https://api.orange.com/v1')
ORANGE_CLIENT_ID = os.getenv('ORANGE_CLIENT_ID')
ORANGE_CLIENT_SECRET = os.getenv('ORANGE_CLIENT_SECRET')

# Initialize client
orange_client = OrangeClient(ORANGE_BASE_URL, ORANGE_CLIENT_ID, ORANGE_CLIENT_SECRET)

# Create Blueprint
orange_bp = Blueprint('orange', __name__)

@orange_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'adapter': 'orange'})

@orange_bp.route('/mobile-payment', methods=['POST'])
def mobile_payment():
    """Process Orange Money payment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'phone_number', 'pin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process payment
        result = orange_client.mobile_payment(
            amount=data['amount'],
            phone_number=data['phone_number'],
            pin=data['pin']
        )
        
        return jsonify({
            'success': True,
            'transaction_id': result.get('transaction_id'),
            'status': result.get('status'),
            'adapter': 'orange'
        })
        
    except Exception as e:
        logger.error(f"Orange Money payment error: {e}")
        return jsonify({'error': str(e)}), 500

@orange_bp.route('/balance', methods=['GET'])
def get_balance():
    """Get Orange Money balance"""
    try:
        balance = orange_client.get_balance()
        return jsonify({
            'success': True,
            'balance': balance,
            'adapter': 'orange'
        })
    except Exception as e:
        logger.error(f"Orange balance error: {e}")
        return jsonify({'error': str(e)}), 500

@orange_bp.route('/transaction/<transaction_id>', methods=['GET'])
def check_transaction(transaction_id):
    """Check transaction status"""
    try:
        transaction = orange_client.check_transaction(transaction_id)
        return jsonify({
            'success': True,
            'transaction': transaction,
            'adapter': 'orange'
        })
    except Exception as e:
        logger.error(f"Orange transaction check error: {e}")
        return jsonify({'error': str(e)}), 500