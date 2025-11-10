import stripe
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StripeClient:
    """
    Client pour interagir avec l'API Stripe
    Gère les paiements, les remboursements et la gestion des clients
    """
    
    def __init__(self, api_key: str):
        """
        Initialise le client Stripe avec la clé API
        
        Args:
            api_key: Clé API secrète Stripe
        """
        self.api_key = api_key
        stripe.api_key = api_key
    
    def create_payment_intent(self, amount: int, currency: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Crée un Payment Intent pour initier un paiement
        
        Args:
            amount: Montant en cents (ex: 1000 pour 10.00€)
            currency: Devise (eur, usd, etc.)
            customer_id: ID du client Stripe existant (optionnel)
            
        Returns:
            Payment Intent créé
        """
        try:
            # Préparation des paramètres du paiement
            intent_params = {
                'amount': amount,
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                }
            }
            
            # Ajout du client si fourni
            if customer_id:
                intent_params['customer'] = customer_id
            
            # Création du Payment Intent
            payment_intent = stripe.PaymentIntent.create(**intent_params)
            
            logger.info(f"Payment Intent créé: {payment_intent.id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création du Payment Intent: {e}")
            raise Exception(f"Échec création Payment Intent: {e}")
    
    def confirm_payment(self, payment_intent_id: str, payment_method: str) -> Dict[str, Any]:
        """
        Confirme un paiement Stripe
        
        Args:
            payment_intent_id: ID du Payment Intent à confirmer
            payment_method: Méthode de paiement à utiliser
            
        Returns:
            Payment Intent confirmé
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method
            )
            
            logger.info(f"Paiement confirmé: {payment_intent.id}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la confirmation: {e}")
            raise Exception(f"Échec confirmation paiement: {e}")
    
    def create_customer(self, email: str, name: str) -> Dict[str, Any]:
        """
        Crée un client Stripe pour paiements futurs
        
        Args:
            email: Email du client
            name: Nom du client
            
        Returns:
            Client Stripe créé
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            
            logger.info(f"Client créé: {customer.id}")
            return customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors de la création du client: {e}")
            raise Exception(f"Échec création client: {e}")
    
    def create_refund(self, payment_intent_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Crée un remboursement pour un paiement
        
        Args:
            payment_intent_id: ID du Payment Intent à rembourser
            amount: Montant à rembourser en cents (optionnel, total par défaut)
            
        Returns:
            Remboursement créé
        """
        try:
            refund_params = {'payment_intent': payment_intent_id}
            if amount:
                refund_params['amount'] = amount
            
            refund = stripe.Refund.create(**refund_params)
            
            logger.info(f"Remboursement créé: {refund.id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe lors du remboursement: {e}")
            raise Exception(f"Échec remboursement: {e}")
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un Payment Intent
        
        Args:
            payment_intent_id: ID du Payment Intent
            
        Returns:
            Détails du Payment Intent
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe récupération Payment Intent: {e}")
            raise Exception(f"Échec récupération Payment Intent: {e}")