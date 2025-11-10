import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MixxClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def send_money(self, amount: float, phone_number: str, description: str) -> Dict[str, Any]:
        """Send money via Mixx"""
        try:
            payload = {
                'amount': amount,
                'phone_number': phone_number,
                'description': description
            }
            
            response = self.session.post(
                f"{self.base_url}/transfers",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Mixx API error: {e}")
            raise
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = self.session.get(f"{self.base_url}/account", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Mixx account info error: {e}")
            raise
    
    def verify_transaction(self, transaction_ref: str) -> Dict[str, Any]:
        """Verify transaction status"""
        try:
            response = self.session.get(
                f"{self.base_url}/transactions/{transaction_ref}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Mixx transaction verification error: {e}")
            raise