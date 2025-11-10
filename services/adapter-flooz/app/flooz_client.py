import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FloozClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def process_payment(self, amount: float, recipient: str, reference: str) -> Dict[str, Any]:
        """Process a payment through Flooz"""
        try:
            payload = {
                'amount': amount,
                'recipient': recipient,
                'reference': reference
            }
            
            response = self.session.post(
                f"{self.base_url}/payments",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Flooz API error: {e}")
            raise
    
    def check_balance(self) -> Dict[str, Any]:
        """Check account balance"""
        try:
            response = self.session.get(f"{self.base_url}/balance", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Flooz balance check error: {e}")
            raise
    
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""
        try:
            response = self.session.get(
                f"{self.base_url}/transactions/{transaction_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Flooz transaction status error: {e}")
            raise