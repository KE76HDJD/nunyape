import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PayPalClient:
    """
    Client pour interagir avec l'API PayPal
    Gère l'authentification et les opérations de paiement
    """
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """
        Initialise le client PayPal avec les credentials
        
        Args:
            base_url: URL de base de l'API PayPal
            client_id: ID client pour l'authentification
            client_secret: Secret client pour l'authentification
        """
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.session = requests.Session()
    
    def _authenticate(self) -> str:
        """
        Authentification OAuth2 avec PayPal
        Retourne le token d'accès
        
        Returns:
            Token d'accès JWT
            
        Raises:
            Exception: Si l'authentification échoue
        """
        try:
            # Préparation des données d'authentification
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            # Requête d'authentification
            response = self.session.post(
                f"{self.base_url}/v1/oauth2/token",
                data=auth_data,
                auth=(self.client_id, self.client_secret),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Mise à jour des headers de session
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            
            logger.info("Authentification PayPal réussie")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur d'authentification PayPal: {e}")
            raise Exception(f"Échec de l'authentification PayPal: {e}")
    
    def create_payment(self, amount: float, currency: str, return_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Crée un paiement PayPal
        
        Args:
            amount: Montant du paiement
            currency: Devise (EUR, USD, etc.)
            return_url: URL de retour après paiement réussi
            cancel_url: URL d'annulation
            
        Returns:
            Données de la transaction PayPal
        """
        try:
            # Vérification et renouvellement du token si nécessaire
            if not self.access_token:
                self._authenticate()
            
            # Préparation du payload de paiement
            payload = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    }
                }],
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                }
            }
            
            # Création du paiement
            response = self.session.post(
                f"{self.base_url}/v1/payments/payment",
                json=payload,
                timeout=30
            )
            
            # Régénération du token en cas d'expiration
            if response.status_code == 401:
                self._authenticate()
                response = self.session.post(
                    f"{self.base_url}/v1/payments/payment",
                    json=payload,
                    timeout=30
                )
            
            response.raise_for_status()
            payment_data = response.json()
            
            logger.info(f"Paiement PayPal créé: {payment_data.get('id')}")
            return payment_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur création paiement PayPal: {e}")
            raise Exception(f"Échec création paiement PayPal: {e}")
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """
        Exécute un paiement PayPal après approbation utilisateur
        
        Args:
            payment_id: ID du paiement à exécuter
            payer_id: ID du payeur
            
        Returns:
            Statut d'exécution du paiement
        """
        try:
            if not self.access_token:
                self._authenticate()
            
            payload = {"payer_id": payer_id}
            
            response = self.session.post(
                f"{self.base_url}/v1/payments/payment/{payment_id}/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 401:
                self._authenticate()
                response = self.session.post(
                    f"{self.base_url}/v1/payments/payment/{payment_id}/execute",
                    json=payload,
                    timeout=30
                )
            
            response.raise_for_status()
            execution_data = response.json()
            
            logger.info(f"Paiement PayPal exécuté: {payment_id}")
            return execution_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur exécution paiement PayPal: {e}")
            raise Exception(f"Échec exécution paiement PayPal: {e}")
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un paiement
        
        Args:
            payment_id: ID du paiement
            
        Returns:
            Détails du paiement
        """
        try:
            if not self.access_token:
                self._authenticate()
            
            response = self.session.get(
                f"{self.base_url}/v1/payments/payment/{payment_id}",
                timeout=30
            )
            
            if response.status_code == 401:
                self._authenticate()
                response = self.session.get(
                    f"{self.base_url}/v1/payments/payment/{payment_id}",
                    timeout=30
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur récupération détails paiement: {e}")
            raise Exception(f"Échec récupération détails paiement: {e}")