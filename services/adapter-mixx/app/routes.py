from flask import Blueprint, request, jsonify
from mixx_client import MixxClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
MIXX_BASE_URL = os.getenv('MIXX_BASE_URL', 'https://api.mixx.ml/v1')
MIXX_API_KEY = os.getenv('MIXX_API_KEY')

# Initialize client
mixx_client = MixxClient(MIXX_BASE_URL, MIXX_API_KEY)

# Create Blueprint
mixx_bp = Blueprint('mixx', __name__)

@mixx_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'adapter': 'mixx'})

@mixx_bp.route('/transfer', methods=['POST'])
def transfer_money():
    """Transfer money via Mixx"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'phone_number', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process transfer
        result = mixx_client.send_money(
            amount=data['amount'],
            phone_number=data['phone_number'],
            description=data['description']
        )
        
        return jsonify({
            'success': True,
            'transaction_ref': result.get('transaction_ref'),
            'status': result.get('status'),
            'adapter': 'mixx'
        })
        
    except Exception as e:
        logger.error(f"Transfer processing error: {e}")
        return jsonify({'error': str(e)}), 500

@mixx_bp.route('/account', methods=['GET'])
def get_account_info():
    """Get account information"""
    try:
        account_info = mixx_client.get_account_info()
        return jsonify({
            'success': True,
            'account': account_info,
            'adapter': 'mixx'
        })
    except Exception as e:
        logger.error(f"Account info error: {e}")
        return jsonify({'error': str(e)}), 500

@mixx_bp.route('/transaction/<transaction_ref>', methods=['GET'])
def verify_transaction(transaction_ref):
    """Verify transaction status"""
    try:
        transaction = mixx_client.verify_transaction(transaction_ref)
        return jsonify({
            'success': True,
            'transaction': transaction,
            'adapter': 'mixx'
        })
    except Exception as e:
        logger.error(f"Transaction verification error: {e}")
        return jsonify({'error': str(e)}), 500