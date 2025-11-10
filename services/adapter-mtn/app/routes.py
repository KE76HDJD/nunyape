from flask import Blueprint, request, jsonify
from min_client import MinClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
MIN_BASE_URL = os.getenv('MIN_BASE_URL', 'https://api.min.com/v1')
MIN_API_KEY = os.getenv('MIN_API_KEY')

# Initialize client
min_client = MinClient(MIN_BASE_URL, MIN_API_KEY)

# Create Blueprint
min_bp = Blueprint('min', __name__)

@min_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'adapter': 'min'})

@min_bp.route('/payment', methods=['POST'])
def create_payment():
    """Create payment via Min"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'currency', 'customer_email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create payment
        result = min_client.create_payment(
            amount=data['amount'],
            currency=data['currency'],
            customer_email=data['customer_email']
        )
        
        return jsonify({
            'success': True,
            'payment_id': result.get('payment_id'),
            'status': result.get('status'),
            'payment_url': result.get('payment_url'),
            'adapter': 'min'
        })
        
    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        return jsonify({'error': str(e)}), 500

@min_bp.route('/wallet', methods=['GET'])
def get_wallet_balance():
    """Get wallet balance"""
    try:
        wallet_info = min_client.get_wallet_balance()
        return jsonify({
            'success': True,
            'wallet': wallet_info,
            'adapter': 'min'
        })
    except Exception as e:
        logger.error(f"Wallet balance error: {e}")
        return jsonify({'error': str(e)}), 500

@min_bp.route('/payment/<payment_id>', methods=['GET'])
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        payment = min_client.check_payment_status(payment_id)
        return jsonify({
            'success': True,
            'payment': payment,
            'adapter': 'min'
        })
    except Exception as e:
        logger.error(f"Payment status error: {e}")
        return jsonify({'error': str(e)}), 500