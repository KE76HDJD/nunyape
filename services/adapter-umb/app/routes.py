from flask import Blueprint, request, jsonify
from umb_client import UMBClient
import os
import logging

logger = logging.getLogger(__name__)

# Configuration
UMB_BASE_URL = os.getenv('UMB_BASE_URL', 'https://api.umb.com/v1')
UMB_API_KEY = os.getenv('UMB_API_KEY')
UMB_MERCHANT_ID = os.getenv('UMB_MERCHANT_ID')

# Initialisation du client
umb_client = UMBClient(UMB_BASE_URL, UMB_API_KEY, UMB_MERCHANT_ID)

# Création du blueprint
umb_bp = Blueprint('umb', __name__)

@umb_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé UMB"""
    return jsonify({'status': 'healthy', 'adapter': 'umb'})

@umb_bp.route('/transfer/mobile', methods=['POST'])
def mobile_transfer():
    """Effectue un transfert mobile"""
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'phone_number', 'reference']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        result = umb_client.mobile_transfer(
            amount=data['amount'],
            phone_number=data['phone_number'],
            reference=data['reference']
        )
        
        return jsonify({
            'success': True,
            'transaction_id': result.get('transaction_id'),
            'status': result.get('status'),
            'adapter': 'umb'
        })
        
    except Exception as e:
        logger.error(f"Erreur transfert mobile UMB: {e}")
        return jsonify({'error': str(e)}), 500

@umb_bp.route('/transfer/bank', methods=['POST'])
def bank_transfer():
    """Effectue un transfert bancaire"""
    try:
        data = request.get_json()
        
        required_fields = ['amount', 'account_number', 'bank_code', 'reference']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ manquant: {field}'}), 400
        
        result = umb_client.bank_transfer(
            amount=data['amount'],
            account_number=data['account_number'],
            bank_code=data['bank_code'],
            reference=data['reference']
        )
        
        return jsonify({
            'success': True,
            'transfer_id': result.get('transfer_id'),
            'status': result.get('status'),
            'adapter': 'umb'
        })
        
    except Exception as e:
        logger.error(f"Erreur transfert bancaire UMB: {e}")
        return jsonify({'error': str(e)}), 500

@umb_bp.route('/balance', methods=['GET'])
def get_balance():
    """Récupère le solde du compte"""
    try:
        balance = umb_client.get_account_balance()
        return jsonify({
            'success': True,
            'balance': balance,
            'adapter': 'umb'
        })
    except Exception as e:
        logger.error(f"Erreur récupération solde UMB: {e}")
        return jsonify({'error': str(e)}), 500

@umb_bp.route('/transaction/<transaction_id>', methods=['GET'])
def get_transaction_status(transaction_id):
    """Vérifie le statut d'une transaction"""
    try:
        transaction = umb_client.check_transaction_status(transaction_id)
        return jsonify({
            'success': True,
            'transaction': transaction,
            'adapter': 'umb'
        })
    except Exception as e:
        logger.error(f"Erreur vérification transaction UMB: {e}")
        return jsonify({'error': str(e)}), 500