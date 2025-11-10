import logging
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Gestionnaire des notifications de facturation
    Envoie des emails pour les factures, rappels de paiement, etc.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de notifications"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@nunyape.com')
    
    def send_invoice_created(self, customer_email: str, customer_name: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Envoie une notification de création de facture
        
        Args:
            customer_email: Email du client
            customer_name: Nom du client
            invoice_data: Données de la facture
            
        Returns:
            bool: True si l'envoi a réussi
        """
        subject = f"Votre facture {invoice_data['invoice_number']} - NUNYAPE"
        
        # Construction du contenu HTML
        html_content = self._generate_invoice_email_template(
            customer_name, 
            invoice_data, 
            "created"
        )
        
        return self._send_email(customer_email, subject, html_content)
    
    def send_payment_reminder(self, customer_email: str, customer_name: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Envoie un rappel de paiement
        
        Args:
            customer_email: Email du client
            customer_name: Nom du client
            invoice_data: Données de la facture
            
        Returns:
            bool: True si l'envoi a réussi
        """
        subject = f"Rappel de paiement - Facture {invoice_data['invoice_number']}"
        
        html_content = self._generate_invoice_email_template(
            customer_name, 
            invoice_data, 
            "reminder"
        )
        
        return self._send_email(customer_email, subject, html_content)
    
    def send_payment_confirmation(self, customer_email: str, customer_name: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Envoie une confirmation de paiement
        
        Args:
            customer_email: Email du client
            customer_name: Nom du client
            invoice_data: Données de la facture
            
        Returns:
            bool: True si l'envoi a réussi
        """
        subject = f"Confirmation de paiement - Facture {invoice_data['invoice_number']}"
        
        html_content = self._generate_invoice_email_template(
            customer_name, 
            invoice_data, 
            "payment_confirmation"
        )
        
        return self._send_email(customer_email, subject, html_content)
    
    def send_overdue_notice(self, customer_email: str, customer_name: str, invoice_data: Dict[str, Any]) -> bool:
        """
        Envoie un avis de retard de paiement
        
        Args:
            customer_email: Email du client
            customer_name: Nom du client
            invoice_data: Données de la facture
            
        Returns:
            bool: True si l'envoi a réussi
        """
        subject = f"URGENT: Facture en retard - {invoice_data['invoice_number']}"
        
        html_content = self._generate_invoice_email_template(
            customer_name, 
            invoice_data, 
            "overdue"
        )
        
        return self._send_email(customer_email, subject, html_content)
    
    def _generate_invoice_email_template(self, customer_name: str, invoice_data: Dict[str, Any], template_type: str) -> str:
        """
        Génère le template HTML pour les emails de facturation
        
        Args:
            customer_name: Nom du client
            invoice_data: Données de la facture
            template_type: Type de template
            
        Returns:
            str: Contenu HTML de l'email
        """
        # Messages selon le type de template
        messages = {
            "created": {
                "title": "Nouvelle facture créée",
                "message": "Votre facture a été créée et est maintenant disponible."
            },
            "reminder": {
                "title": "Rappel de paiement",
                "message": "Rappel amical : votre facture arrive à échéance bientôt."
            },
            "payment_confirmation": {
                "title": "Paiement confirmé",
                "message": "Nous avons bien reçu votre paiement. Merci !"
            },
            "overdue": {
                "title": "FACTURE EN RETARD",
                "message": "ATTENTION : Votre facture est en retard de paiement."
            }
        }
        
        template_info = messages.get(template_type, messages["created"])
        
        # Génération du HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .invoice-details {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .button {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
                .urgent {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NUNYAPE</h1>
                    <h2>{template_info['title']}</h2>
                </div>
                
                <div class="content">
                    <p>Bonjour {customer_name},</p>
                    
                    <p>{template_info['message']}</p>
                    
                    <div class="invoice-details">
                        <h3>Détails de la facture :</h3>
                        <p><strong>Numéro :</strong> {invoice_data['invoice_number']}</p>
                        <p><strong>Date d'émission :</strong> {invoice_data['issue_date']}</p>
                        <p><strong>Date d'échéance :</strong> {invoice_data['due_date']}</p>
                        <p><strong>Montant total :</strong> {invoice_data['total_amount']} {invoice_data['currency']}</p>
                        {"<p class='urgent'>Cette facture est en retard de paiement. Veuillez régulariser votre situation dès que possible.</p>" if template_type == "overdue" else ""}
                    </div>
                    
                    <p>
                        <a href="{os.getenv('BILLING_PORTAL_URL', 'https://billing.nunyape.com')}/invoices/{invoice_data['invoice_id']}" class="button">
                            Voir la facture
                        </a>
                    </p>
                    
                    <p>Pour toute question, n'hésitez pas à répondre à cet email.</p>
                    
                    <p>Cordialement,<br>L'équipe NUNYAPE</p>
                </div>
                
                <div class="footer">
                    <p>NUNYAPE SAS - RCS Paris 123 456 789</p>
                    <p>123 Avenue de la République, 75011 Paris, France</p>
                    <p>Email: contact@nunyape.com - Tél: +33 1 23 45 67 89</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Envoie un email via SMTP
        
        Args:
            to_email: Email du destinataire
            subject: Sujet de l'email
            html_content: Contenu HTML de l'email
            
        Returns:
            bool: True si l'envoi a réussi
        """
        try:
            # Création du message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Partie HTML
            html_part = MimeText(html_content, 'html')
            msg.attach(html_part)
            
            # Connexion au serveur SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email envoyé avec succès à {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email à {to_email}: {e}")
            return False
    
    def send_batch_notifications(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Envoie un lot de notifications
        
        Args:
            notifications: Liste des notifications à envoyer
            
        Returns:
            Dict: Résultat de l'envoi groupé
        """
        results = {
            'total': len(notifications),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for notification in notifications:
            notification_type = notification['type']
            customer_email = notification['customer_email']
            customer_name = notification['customer_name']
            invoice_data = notification['invoice_data']
            
            success = False
            
            try:
                if notification_type == 'invoice_created':
                    success = self.send_invoice_created(customer_email, customer_name, invoice_data)
                elif notification_type == 'payment_reminder':
                    success = self.send_payment_reminder(customer_email, customer_name, invoice_data)
                elif notification_type == 'payment_confirmation':
                    success = self.send_payment_confirmation(customer_email, customer_name, invoice_data)
                elif notification_type == 'overdue_notice':
                    success = self.send_overdue_notice(customer_email, customer_name, invoice_data)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Échec envoi à {customer_email}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Erreur avec {customer_email}: {str(e)}")
                logger.error(f"Erreur notification batch: {e}")
        
        return results