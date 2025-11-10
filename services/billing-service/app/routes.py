from flask import Blueprint, request, jsonify, send_file
from .models import Customer, Invoice, Subscription, BillingPlan, InvoiceStatus, PaymentMethod
from .notifications import NotificationManager
from .pdf_generator import PDFGenerator
import logging
import uuid
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Initialisation des composants
notification_manager = NotificationManager()
pdf_generator = PDFGenerator()

# Stockage en mémoire (à remplacer par une base de données)
customers_store = {}
invoices_store = {}
subscriptions_store = {}

# Création du blueprint
billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé du service de facturation
    """
    return jsonify({
        'status': 'healthy',
        'service': 'billing-service',
        'timestamp': datetime.utcnow().isoformat(),
        'stats': {
            'customers': len(customers_store),
            'invoices': len(invoices_store),
            'subscriptions': len(subscriptions_store)
        }
    })

@billing_bp.route('/customers', methods=['POST'])
def create_customer():
    """
    Crée un nouveau client
    
    Body JSON attendu:
        - email: Email du client
        - name: Nom du client
        - company: Entreprise (optionnel)
        - phone: Téléphone (optionnel)
        - address: Adresse (optionnel)
        - tax_number: Numéro de taxe (optionnel)
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['email', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400
        
        # Vérification de l'unicité de l'email
        for existing_customer in customers_store.values():
            if existing_customer.email == data['email']:
                return jsonify({'error': 'Un client avec cet email existe déjà'}), 409
        
        # Création du client
        customer_id = str(uuid.uuid4())
        customer = Customer(customer_id, data['email'], data['name'], data.get('company'))
        
        # Informations de contact optionnelles
        if data.get('phone') or data.get('address'):
            customer.set_contact_info(
                phone=data.get('phone'),
                address=data.get('address', {}),
                tax_number=data.get('tax_number')
            )
        
        customers_store[customer_id] = customer
        
        logger.info(f"Client créé: {customer_id} - {data['email']}")
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict(),
            'message': 'Client créé avec succès'
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur création client: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """
    Récupère les informations d'un client
    
    Args:
        customer_id: ID du client
    """
    try:
        customer = customers_store.get(customer_id)
        
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        return jsonify({
            'success': True,
            'customer': customer.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération client: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/invoices', methods=['POST'])
def create_invoice():
    """
    Crée une nouvelle facture
    
    Body JSON attendu:
        - customer_id: ID du client
        - amount: Montant de la facture
        - currency: Devise (optionnel, défaut: EUR)
        - items: Liste des articles (optionnel)
        - due_days: Jours jusqu'à l'échéance (optionnel, défaut: 30)
    """
    try:
        data = request.get_json()
        
        # Validation des champs obligatoires
        required_fields = ['customer_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400
        
        # Vérification de l'existence du client
        customer = customers_store.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        # Création de la facture
        invoice_id = str(uuid.uuid4())
        invoice = Invoice(
            invoice_id=invoice_id,
            customer_id=data['customer_id'],
            amount=data['amount'],
            currency=data.get('currency', 'EUR')
        )
        
        # Configuration de la date d'échéance
        due_days = data.get('due_days', 30)
        invoice.set_due_date(due_days)
        
        # Ajout des articles si fournis
        if 'items' in data:
            for item in data['items']:
                invoice.add_item(
                    description=item['description'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price'],
                    tax_rate=item.get('tax_rate')
                )
        
        invoices_store[invoice_id] = invoice
        
        # Envoi de notification
        notification_manager.send_invoice_created(
            customer_email=customer.email,
            customer_name=customer.name,
            invoice_data=invoice.to_dict()
        )
        
        logger.info(f"Facture créée: {invoice_id} pour le client {data['customer_id']}")
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict(),
            'message': 'Facture créée avec succès'
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur création facture: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/invoices/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """
    Récupère une facture
    
    Args:
        invoice_id: ID de la facture
    """
    try:
        invoice = invoices_store.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Facture non trouvée'}), 404
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Erreur récupération facture: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/invoices/<invoice_id>/pdf', methods=['GET'])
def get_invoice_pdf(invoice_id):
    """
    Génère et retourne le PDF d'une facture
    
    Args:
        invoice_id: ID de la facture
    """
    try:
        invoice = invoices_store.get(invoice_id)
        
        if not invoice:
            return jsonify({'error': 'Facture non trouvée'}), 404
        
        customer = customers_store.get(invoice.customer_id)
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        # Génération du PDF
        pdf_path = pdf_generator.generate_invoice_pdf(
            invoice.to_dict(),
            customer.to_dict()
        )
        
        if not pdf_path:
            return jsonify({'error': 'Erreur génération PDF'}), 500
        
        # Retour du fichier PDF
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"facture_{invoice.invoice_number}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erreur génération PDF facture: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/invoices/<invoice_id>/pay', methods=['POST'])
def record_payment(invoice_id):
    """
    Enregistre un paiement pour une facture
    
    Body JSON attendu:
        - payment_method: Méthode de paiement
        - amount: Montant payé
        - transaction_id: ID de transaction externe
    """
    try:
        data = request.get_json()
        
        required_fields = ['payment_method', 'amount', 'transaction_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400
        
        invoice = invoices_store.get(invoice_id)
        if not invoice:
            return jsonify({'error': 'Facture non trouvée'}), 404
        
        customer = customers_store.get(invoice.customer_id)
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        # Validation de la méthode de paiement
        try:
            payment_method = PaymentMethod(data['payment_method'])
        except ValueError:
            return jsonify({'error': 'Méthode de paiement invalide'}), 400
        
        # Enregistrement du paiement
        invoice.add_payment(
            payment_method=payment_method,
            amount=data['amount'],
            transaction_id=data['transaction_id']
        )
        
        # Envoi de confirmation
        if invoice.status == InvoiceStatus.PAID:
            notification_manager.send_payment_confirmation(
                customer_email=customer.email,
                customer_name=customer.name,
                invoice_data=invoice.to_dict()
            )
        
        logger.info(f"Paiement enregistré pour la facture {invoice_id}: {data['amount']} {invoice.currency}")
        
        return jsonify({
            'success': True,
            'invoice': invoice.to_dict(),
            'message': 'Paiement enregistré avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur enregistrement paiement: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """
    Crée un nouvel abonnement
    
    Body JSON attendu:
        - customer_id: ID du client
        - plan: Plan d'abonnement
    """
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'plan']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400
        
        customer = customers_store.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Client non trouvé'}), 404
        
        # Validation du plan
        try:
            plan = BillingPlan(data['plan'])
        except ValueError:
            return jsonify({'error': 'Plan d\'abonnement invalide'}), 400
        
        # Création de l'abonnement
        subscription_id = str(uuid.uuid4())
        subscription = Subscription(
            subscription_id=subscription_id,
            customer_id=data['customer_id'],
            plan=plan
        )
        
        subscriptions_store[subscription_id] = subscription
        
        logger.info(f"Abonnement créé: {subscription_id} - Plan: {plan.value}")
        
        return jsonify({
            'success': True,
            'subscription': subscription.to_dict(),
            'message': 'Abonnement créé avec succès'
        }), 201
        
    except Exception as e:
        logger.error(f"Erreur création abonnement: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/notifications/reminders', methods=['POST'])
def send_payment_reminders():
    """
    Envoie des rappels de paiement pour les factures en attente
    """
    try:
        reminders_sent = 0
        errors = []
        
        for invoice in invoices_store.values():
            if invoice.status == InvoiceStatus.PENDING and not invoice.is_overdue():
                customer = customers_store.get(invoice.customer_id)
                if customer:
                    success = notification_manager.send_payment_reminder(
                        customer_email=customer.email,
                        customer_name=customer.name,
                        invoice_data=invoice.to_dict()
                    )
                    
                    if success:
                        reminders_sent += 1
                    else:
                        errors.append(f"Échec envoi rappel pour {invoice.invoice_number}")
        
        return jsonify({
            'success': True,
            'reminders_sent': reminders_sent,
            'errors': errors,
            'message': f'{reminders_sent} rappels de paiement envoyés'
        })
        
    except Exception as e:
        logger.error(f"Erreur envoi rappels: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/reports/overdue', methods=['GET'])
def get_overdue_invoices():
    """
    Retourne la liste des factures en retard
    """
    try:
        overdue_invoices = []
        
        for invoice in invoices_store.values():
            if invoice.is_overdue() and invoice.status != InvoiceStatus.PAID:
                customer = customers_store.get(invoice.customer_id)
                invoice_data = invoice.to_dict()
                invoice_data['customer'] = customer.to_dict() if customer else None
                overdue_invoices.append(invoice_data)
        
        return jsonify({
            'success': True,
            'overdue_invoices': overdue_invoices,
            'count': len(overdue_invoices),
            'total_amount': sum(inv['total_amount'] for inv in overdue_invoices)
        })
        
    except Exception as e:
        logger.error(f"Erreur rapport factures en retard: {e}")
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/reports/revenue', methods=['GET'])
def get_revenue_report():
    """
    Génère un rapport de revenus
    """
    try:
        # Période par défaut: 30 derniers jours
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        paid_invoices = [
            invoice for invoice in invoices_store.values()
            if invoice.status == InvoiceStatus.PAID and invoice.created_at >= start_date
        ]
        
        total_revenue = sum(invoice.total_amount for invoice in paid_invoices)
        total_invoices = len(paid_invoices)
        
        # Répartition par méthode de paiement
        payment_methods = {}
        for invoice in paid_invoices:
            for payment in invoice.payments:
                method = payment['payment_method']
                payment_methods[method] = payment_methods.get(method, 0) + payment['amount']
        
        return jsonify({
            'success': True,
            'report': {
                'period': f'{days} jours',
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat(),
                'total_revenue': total_revenue,
                'total_invoices': total_invoices,
                'average_invoice_amount': total_revenue / total_invoices if total_invoices > 0 else 0,
                'payment_methods': payment_methods
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur rapport revenus: {e}")
        return jsonify({'error': str(e)}), 500