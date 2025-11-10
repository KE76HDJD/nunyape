import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

class PDFGenerator:
    """
    Générateur de PDF pour les factures et documents de facturation
    """
    
    def __init__(self):
        """Initialise le générateur de PDF"""
        self.output_dir = os.getenv('PDF_OUTPUT_DIR', '/tmp/invoices')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Enregistrement des polices (optionnel)
        try:
            # Vous pouvez ajouter des polices custom ici
            pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
        except:
            logger.warning("Polices custom non disponibles, utilisation des polices par défaut")
    
    def generate_invoice_pdf(self, invoice_data: Dict[str, Any], customer_data: Dict[str, Any]) -> Optional[str]:
        """
        Génère un PDF de facture
        
        Args:
            invoice_data: Données de la facture
            customer_data: Données du client
            
        Returns:
            str: Chemin vers le fichier PDF généré, None en cas d'erreur
        """
        try:
            # Nom du fichier
            filename = f"invoice_{invoice_data['invoice_number']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Création du document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Contenu du document
            story = []
            styles = getSampleStyleSheet()
            
            # Style pour le titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # En-tête
            story.append(Paragraph("FACTURE", title_style))
            
            # Informations de la société et du client
            company_client_table = self._create_company_client_table(customer_data, invoice_data)
            story.append(company_client_table)
            story.append(Spacer(1, 15*mm))
            
            # Détails de la facture
            invoice_details_table = self._create_invoice_details_table(invoice_data)
            story.append(invoice_details_table)
            story.append(Spacer(1, 10*mm))
            
            # Articles de la facture
            items_table = self._create_items_table(invoice_data['items'])
            story.append(items_table)
            story.append(Spacer(1, 10*mm))
            
            # Totaux
            totals_table = self._create_totals_table(invoice_data)
            story.append(totals_table)
            story.append(Spacer(1, 15*mm))
            
            # Notes
            if invoice_data.get('notes'):
                notes_style = ParagraphStyle(
                    'NotesStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.gray,
                    borderPadding=5,
                    borderColor=colors.gray,
                    borderWidth=1
                )
                story.append(Paragraph("Notes:", styles['Heading3']))
                story.append(Paragraph(invoice_data['notes'], notes_style))
            
            # Pied de page
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1  # Centré
            )
            story.append(Spacer(1, 20*mm))
            story.append(Paragraph("NUNYAPE SAS - RCS Paris 123 456 789 - TVA FR 12 345 678 901", footer_style))
            story.append(Paragraph("123 Avenue de la République, 75011 Paris, France - contact@nunyape.com - +33 1 23 45 67 89", footer_style))
            story.append(Paragraph("SAS au capital de 10 000 €", footer_style))
            
            # Génération du PDF
            doc.build(story)
            
            logger.info(f"PDF de facture généré: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur génération PDF facture: {e}")
            return None
    
    def _create_company_client_table(self, customer_data: Dict[str, Any], invoice_data: Dict[str, Any]) -> Table:
        """
        Crée le tableau des informations société/client
        
        Args:
            customer_data: Données du client
            invoice_data: Données de la facture
            
        Returns:
            Table: Tableau formaté
        """
        # Données de la société
        company_data = [
            ["NUNYAPE SAS", ""],
            ["123 Avenue de la République", f"Facture N°: {invoice_data['invoice_number']}"],
            ["75011 Paris, France", f"Date d'émission: {invoice_data['issue_date']}"],
            ["contact@nunyape.com", f"Date d'échéance: {invoice_data['due_date']}"],
            ["+33 1 23 45 67 89", f"Statut: {invoice_data['status'].upper()}"],
            ["RCS Paris 123 456 789", ""],
            ["TVA FR 12 345 678 901", ""]
        ]
        
        # Données du client
        client_data = [
            ["CLIENT:", ""],
            [customer_data['name'], ""],
            [customer_data.get('company', ''), ""],
            [customer_data.get('address', {}).get('line1', ''), ""],
            [f"{customer_data.get('address', {}).get('postal_code', '')} {customer_data.get('address', {}).get('city', '')}", ""],
            [customer_data.get('address', {}).get('country', ''), ""],
            [f"TVA: {customer_data.get('tax_number', 'Non applicable')}", ""]
        ]
        
        # Combinaison des données
        data = []
        max_rows = max(len(company_data), len(client_data))
        
        for i in range(max_rows):
            row = []
            if i < len(company_data):
                row.extend(company_data[i])
            else:
                row.extend(["", ""])
            
            if i < len(client_data):
                row.extend(client_data[i])
            else:
                row.extend(["", ""])
            
            data.append(row)
        
        table = Table(data, colWidths=[60*mm, 60*mm, 40*mm, 40*mm])
        
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 11),
            ('FONT', (2, 0), (2, 0), 'Helvetica-Bold', 11),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#34495e')),
            ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (1, 0), 1, colors.whitesmoke),
            ('LINEBELOW', (2, 0), (3, 0), 1, colors.whitesmoke),
            ('BOX', (0, 0), (1, -1), 1, colors.lightgrey),
            ('BOX', (2, 0), (3, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _create_invoice_details_table(self, invoice_data: Dict[str, Any]) -> Table:
        """
        Crée le tableau des détails de la facture
        
        Args:
            invoice_data: Données de la facture
            
        Returns:
            Table: Tableau formaté
        """
        data = [
            ["DÉTAILS DE LA FACTURE", ""],
            ["Période facturée:", f"{invoice_data.get('billing_period', 'Période standard')}"],
            ["Devise:", invoice_data['currency']],
            ["Taux de TVA:", f"{invoice_data['tax_rate'] * 100}%"],
        ]
        
        table = Table(data, colWidths=[80*mm, 100*mm])
        
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_items_table(self, items: List[Dict[str, Any]]) -> Table:
        """
        Crée le tableau des articles de la facture
        
        Args:
            items: Liste des articles
            
        Returns:
            Table: Tableau formaté
        """
        # En-têtes
        data = [["Description", "Quantité", "Prix unitaire", "TVA", "Total"]]
        
        # Articles
        for item in items:
            data.append([
                item['description'],
                str(item['quantity']),
                f"{item['unit_price']:.2f} €",
                f"{item['tax_rate'] * 100}%",
                f"{item['total']:.2f} €"
            ])
        
        table = Table(data, colWidths=[80*mm, 25*mm, 30*mm, 25*mm, 30*mm])
        
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))
        
        return table
    
    def _create_totals_table(self, invoice_data: Dict[str, Any]) -> Table:
        """
        Crée le tableau des totaux
        
        Args:
            invoice_data: Données de la facture
            
        Returns:
            Table: Tableau formaté
        """
        data = [
            ["SOUS-TOTAL:", f"{invoice_data['amount']:.2f} €"],
            [f"TVA ({invoice_data['tax_rate'] * 100}%):", f"{invoice_data['tax_amount']:.2f} €"],
            ["TOTAL:", f"<b>{invoice_data['total_amount']:.2f} €</b>"]
        ]
        
        table = Table(data, colWidths=[100*mm, 60*mm])
        
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 2), (-1, 2), 'Helvetica-Bold', 12),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.lightgrey),
            ('LINEABOVE', (0, 2), (-1, 2), 2, colors.black),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        
        return table
    
    def generate_receipt_pdf(self, payment_data: Dict[str, Any], invoice_data: Dict[str, Any]) -> Optional[str]:
        """
        Génère un reçu de paiement
        
        Args:
            payment_data: Données du paiement
            invoice_data: Données de la facture
            
        Returns:
            str: Chemin vers le fichier PDF généré
        """
        try:
            filename = f"receipt_{payment_data['payment_id']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Logique similaire à generate_invoice_pdf mais pour un reçu
            # Implémentation simplifiée pour l'exemple
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            story.append(Paragraph("REÇU DE PAIEMENT", styles['Heading1']))
            story.append(Spacer(1, 20))
            
            # Ajouter les détails du paiement...
            
            doc.build(story)
            
            logger.info(f"PDF de reçu généré: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erreur génération PDF reçu: {e}")
            return None