import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class UMBClient:
    """
    Client pour l'API UMB (United Mobile Banking)
    Spécialisé dans les transferts mobiles et les services bancaires
    """
    
    def __init__(self, base_url: str, api_key: str, merchant_id: str):
        """
        Initialise le client UMB
        
        Args:
            base_url: URL de base de l'API UMB
            api_key: Clé API pour l'authentification
            merchant_id: ID du marchand UMB
        """
        self.base_url = base_url
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'X-Merchant-ID': merchant_id,
            'Content-Type': 'application/json'
        })
    
    def mobile_transfer(self, amount: float, phone_number: str, reference: str) -> Dict[str, Any]:
        """
        Effectue un transfert mobile via UMB
        
        Args:
            amount: Montant du transfert
            phone_number: Numéro de téléphone du bénéficiaire
            reference: Référence unique de la transaction
            
        Returns:
            Détails de la transaction
        """
        try:
            payload = {
                'amount': amount,
                'recipient_phone': phone_number,
                'transaction_reference': reference,
                'currency': 'XOF'
            }
            
            response = self.session.post(
                f"{self.base_url}/transfers/mobile",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            transaction_data = response.json()
            logger.info(f"Transfert UMB effectué: {transaction_data.get('transaction_id')}")
            return transaction_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur transfert UMB: {e}")
            raise Exception(f"Échec transfert UMB: {e}")
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Récupère le solde du compte marchand
        
        Returns:
            Informations de solde
        """
        try:
            response = self.session.get(f"{self.base_url}/account/balance", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur récupération solde UMB: {e}")
            raise Exception(f"Échec récupération solde: {e}")
    
    def check_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Vérifie le statut d'une transaction
        
        Args:
            transaction_id: ID de la transaction à vérifier
            
        Returns:
            Statut de la transaction
        """
        try:
            response = self.session.get(
                f"{self.base_url}/transactions/{transaction_id}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur vérification transaction UMB: {e}")
            raise Exception(f"Échec vérification transaction: {e}")
    
    def bank_transfer(self, amount: float, account_number: str, bank_code: str, reference: str) -> Dict[str, Any]:
        """
        Effectue un transfert bancaire via UMB
        
        Args:
            amount: Montant du transfert
            account_number: Numéro de compte bancaire
            bank_code: Code de la banque destinataire
            reference: Référence de la transaction
            
        Returns:
            Détails du transfert bancaire
        """
        try:
            payload = {
                'amount': amount,
                'account_number': account_number,
                'bank_code': bank_code,
                'transaction_reference': reference,
                'currency': 'XOF'
            }
            
            response = self.session.post(
                f"{self.base_url}/transfers/bank",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            transfer_data = response.json()
            logger.info(f"Transfert bancaire UMB effectué: {transfer_data.get('transfer_id')}")
            return transfer_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur transfert bancaire UMB: {e}")
            raise Exception(f"Échec transfert bancaire: {e}")