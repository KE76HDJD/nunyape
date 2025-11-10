import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MinClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        })
    
    def create_payment(self, amount: float, currency: str, customer_email: str) -> Dict[str, Any]:
        """Create a payment via Min"""
        try:
            payload = {
                'amount': amount,
                'currency': currency,
                'customer_email': customer_email
            }
            
            response = self.session.post(
                f"{self.base_url}/payments",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Min API error: {e}")
            raise
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            response = self.session.get(f"{self.base_url}/wallet", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Min wallet balance error: {e}")
            raise
    
    def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Check payment status"""
        try:
            response = self.session.get(
                f"{self.base_url}/payments/{payment_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Min payment status error: {e}")
            raise