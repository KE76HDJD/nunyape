import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OrangeClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.session = requests.Session()
    
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            auth_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            response = self.session.post(
                f"{self.base_url}/oauth/token",
                data=auth_data,
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Update session headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Orange authentication error: {e}")
            raise
    
    def mobile_payment(self, amount: float, phone_number: str, pin: str) -> Dict[str, Any]:
        """Process mobile payment via Orange Money"""
        try:
            # Ensure we have a valid token
            if not self.access_token:
                self.authenticate()
            
            payload = {
                'amount': amount,
                'phone_number': phone_number,
                'pin': pin
            }
            
            response = self.session.post(
                f"{self.base_url}/mobile-payments",
                json=payload,
                timeout=30
            )
            
            # If token expired, reauthenticate and retry
            if response.status_code == 401:
                self.authenticate()
                response = self.session.post(
                    f"{self.base_url}/mobile-payments",
                    json=payload,
                    timeout=30
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Orange Money API error: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Get Orange Money balance"""
        try:
            if not self.access_token:
                self.authenticate()
                
            response = self.session.get(f"{self.base_url}/balance", timeout=30)
            
            if response.status_code == 401:
                self.authenticate()
                response = self.session.get(f"{self.base_url}/balance", timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Orange balance error: {e}")
            raise
    
    def check_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Check transaction status"""
        try:
            if not self.access_token:
                self.authenticate()
                
            response = self.session.get(
                f"{self.base_url}/transactions/{transaction_id}",
                timeout=30
            )
            
            if response.status_code == 401:
                self.authenticate()
                response = self.session.get(
                    f"{self.base_url}/transactions/{transaction_id}",
                    timeout=30
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Orange transaction check error: {e}")
            raise