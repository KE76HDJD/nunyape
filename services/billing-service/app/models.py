from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class InvoiceStatus(Enum):
    """Statuts possibles d'une facture"""
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    """Méthodes de paiement supportées"""
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    ORANGE_MONEY = "orange_money"
    MTN_MOBILE_MONEY = "mtn_mobile_money"
    STRIPE = "stripe"

class BillingPlan(Enum):
    """Plans de tarification disponibles"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class Customer:
    """
    Modèle représentant un client pour la facturation
    """
    
    def __init__(self, customer_id: str, email: str, name: str, company: Optional[str] = None):
        """
        Initialise un client
        
        Args:
            customer_id: Identifiant unique du client
            email: Email du client
            name: Nom du client
            company: Entreprise du client (optionnel)
        """
        self.customer_id = customer_id
        self.email = email
        self.name = name
        self.company = company
        self.phone = None
        self.address = None
        self.tax_number = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
    
    def set_contact_info(self, phone: str, address: Dict[str, str], tax_number: Optional[str] = None):
        """
        Définit les informations de contact du client
        
        Args:
            phone: Numéro de téléphone
            address: Adresse postale
            tax_number: Numéro de taxe (optionnel)
        """
        self.phone = phone
        self.address = address
        self.tax_number = tax_number
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le client en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable du client
        """
        return {
            'customer_id': self.customer_id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'phone': self.phone,
            'address': self.address,
            'tax_number': self.tax_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class Invoice:
    """
    Modèle représentant une facture
    """
    
    def __init__(self, invoice_id: str, customer_id: str, amount: float, currency: str = 'EUR'):
        """
        Initialise une facture
        
        Args:
            invoice_id: Identifiant unique de la facture
            customer_id: ID du client
            amount: Montant total de la facture
            currency: Devise (défaut: EUR)
        """
        self.invoice_id = invoice_id
        self.customer_id = customer_id
        self.invoice_number = self._generate_invoice_number()
        self.amount = amount
        self.currency = currency
        self.status = InvoiceStatus.DRAFT
        self.created_at = datetime.utcnow()
        self.issue_date = datetime.utcnow().date()
        self.due_date = (datetime.utcnow() + timedelta(days=30)).date()
        self.items = []
        self.tax_rate = 0.20  # TVA 20% par défaut
        self.tax_amount = 0
        self.total_amount = amount
        self.payments = []
        self.notes = ""
    
    def _generate_invoice_number(self) -> str:
        """
        Génère un numéro de facture unique
        
        Returns:
            str: Numéro de facture formaté
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"INV-{timestamp}-{unique_id}"
    
    def add_item(self, description: str, quantity: int, unit_price: float, tax_rate: Optional[float] = None):
        """
        Ajoute un article à la facture
        
        Args:
            description: Description de l'article
            quantity: Quantité
            unit_price: Prix unitaire
            tax_rate: Taux de taxe (optionnel)
        """
        item_tax_rate = tax_rate if tax_rate is not None else self.tax_rate
        subtotal = quantity * unit_price
        item_tax = subtotal * item_tax_rate
        
        item = {
            'item_id': str(uuid.uuid4()),
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price,
            'tax_rate': item_tax_rate,
            'subtotal': subtotal,
            'tax_amount': item_tax,
            'total': subtotal + item_tax
        }
        
        self.items.append(item)
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalcule les totaux de la facture"""
        self.amount = sum(item['subtotal'] for item in self.items)
        self.tax_amount = sum(item['tax_amount'] for item in self.items)
        self.total_amount = self.amount + self.tax_amount
    
    def set_due_date(self, days: int):
        """
        Définit la date d'échéance
        
        Args:
            days: Nombre de jours jusqu'à l'échéance
        """
        self.due_date = (datetime.utcnow() + timedelta(days=days)).date()
    
    def add_payment(self, payment_method: PaymentMethod, amount: float, transaction_id: str):
        """
        Ajoute un paiement à la facture
        
        Args:
            payment_method: Méthode de paiement
            amount: Montant payé
            transaction_id: ID de transaction
        """
        payment = {
            'payment_id': str(uuid.uuid4()),
            'payment_method': payment_method.value,
            'amount': amount,
            'transaction_id': transaction_id,
            'payment_date': datetime.utcnow(),
            'status': 'completed'
        }
        
        self.payments.append(payment)
        
        # Mise à jour du statut si la facture est entièrement payée
        total_paid = sum(p['amount'] for p in self.payments)
        if total_paid >= self.total_amount:
            self.status = InvoiceStatus.PAID
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la facture en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable de la facture
        """
        return {
            'invoice_id': self.invoice_id,
            'customer_id': self.customer_id,
            'invoice_number': self.invoice_number,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'issue_date': self.issue_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'items': self.items,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'payments': self.payments,
            'notes': self.notes,
            'is_overdue': self.is_overdue()
        }
    
    def is_overdue(self) -> bool:
        """
        Vérifie si la facture est en retard
        
        Returns:
            bool: True si la facture est en retard
        """
        if self.status == InvoiceStatus.PAID:
            return False
        
        return datetime.utcnow().date() > self.due_date

class Subscription:
    """
    Modèle représentant un abonnement
    """
    
    def __init__(self, subscription_id: str, customer_id: str, plan: BillingPlan):
        """
        Initialise un abonnement
        
        Args:
            subscription_id: Identifiant unique de l'abonnement
            customer_id: ID du client
            plan: Plan d'abonnement
        """
        self.subscription_id = subscription_id
        self.customer_id = customer_id
        self.plan = plan
        self.status = 'active'
        self.created_at = datetime.utcnow()
        self.current_period_start = datetime.utcnow()
        self.current_period_end = datetime.utcnow() + timedelta(days=30)
        self.cancel_at_period_end = False
        self.metadata = {}
    
    def cancel(self):
        """Annule l'abonnement à la fin de la période"""
        self.cancel_at_period_end = True
        self.status = 'canceled'
    
    def renew(self):
        """Renouvelle l'abonnement"""
        if self.cancel_at_period_end:
            self.cancel_at_period_end = False
            self.status = 'active'
        
        self.current_period_start = datetime.utcnow()
        self.current_period_end = datetime.utcnow() + timedelta(days=30)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit l'abonnement en dictionnaire
        
        Returns:
            Dict: Représentation sérialisable de l'abonnement
        """
        return {
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'plan': self.plan.value,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'current_period_start': self.current_period_start.isoformat(),
            'current_period_end': self.current_period_end.isoformat(),
            'cancel_at_period_end': self.cancel_at_period_end,
            'metadata': self.metadata
        }