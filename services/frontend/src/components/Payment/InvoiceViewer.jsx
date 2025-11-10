import React, { useState, useEffect } from 'react';
import { Download, Printer, Mail, Calendar, User, Building } from 'lucide-react';
import { uvdaApi } from '../../../services/uvda/api';

const InvoiceViewer = ({ invoiceId, onClose }) => {
  const [invoice, setInvoice] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadInvoice = async () => {
      try {
        // Simuler le chargement d'une facture
        const mockInvoice = {
          id: invoiceId || 'INV-2024-001',
          number: `INV-${new Date().getFullYear()}-${String(invoiceId || '001').padStart(3, '0')}`,
          date: new Date().toISOString().split('T')[0],
          dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          status: 'paid',
          amount: 1999,
          currency: 'EUR',
          customer: {
            name: 'John Doe',
            email: 'john.doe@example.com',
            company: 'Example Corp'
          },
          items: [
            {
              id: 1,
              description: 'Accès présentation premium - "Introduction à React"',
              quantity: 1,
              unitPrice: 1999,
              total: 1999
            }
          ],
          taxRate: 20,
          notes: 'Merci pour votre achat !'
        };
        
        setInvoice(mockInvoice);
      } catch (error) {
        console.error('Erreur lors du chargement:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadInvoice();
  }, [invoiceId]);

  const handlePrint = () => {
    window.print();
  };

  const handleDownload = () => {
    // Générer un PDF de la facture
    alert('Téléchargement de la facture en PDF...');
  };

  const handleEmail = () => {
    // Envoyer la facture par email
    alert('Facture envoyée par email...');
  };

  const formatCurrency = (amount, currency = 'EUR') => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency
    }).format(amount / 100);
  };

  const calculateTax = (amount, taxRate) => {
    return (amount * taxRate) / 100;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Chargement de la facture...</div>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Facture non trouvée</div>
      </div>
    );
  }

  const taxAmount = calculateTax(invoice.amount, invoice.taxRate);
  const totalAmount = invoice.amount + taxAmount;

  return (
    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Facture</h1>
          <p className="text-gray-600">Numéro: {invoice.number}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownload}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Télécharger</span>
          </button>
          
          <button
            onClick={handlePrint}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Printer className="h-4 w-4" />
            <span>Imprimer</span>
          </button>
          
          <button
            onClick={handleEmail}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Mail className="h-4 w-4" />
            <span>Envoyer</span>
          </button>
        </div>
      </div>

      {/* Invoice Content */}
      <div className="p-6">
        {/* Company and Customer Info */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <Building className="h-5 w-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">UVDA Platform</h3>
            </div>
            <p className="text-gray-600">123 Rue de la Présentation</p>
            <p className="text-gray-600">75001 Paris, France</p>
            <p className="text-gray-600">contact@uvda.com</p>
            <p className="text-gray-600">SIRET: 123 456 789 00012</p>
          </div>

          <div>
            <div className="flex items-center space-x-2 mb-2">
              <User className="h-5 w-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Facturé à</h3>
            </div>
            <p className="text-gray-900 font-medium">{invoice.customer.name}</p>
            <p className="text-gray-600">{invoice.customer.email}</p>
            {invoice.customer.company && (
              <p className="text-gray-600">{invoice.customer.company}</p>
            )}
          </div>
        </div>

        {/* Invoice Details */}
        <div className="grid grid-cols-3 gap-6 mb-8 p-4 bg-gray-50 rounded-lg">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Date de facturation</span>
            </div>
            <p className="text-gray-900">{new Date(invoice.date).toLocaleDateString('fr-FR')}</p>
          </div>
          
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Date d'échéance</span>
            </div>
            <p className="text-gray-900">{new Date(invoice.dueDate).toLocaleDateString('fr-FR')}</p>
          </div>
          
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-sm font-medium text-gray-700">Statut</span>
            </div>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              invoice.status === 'paid' 
                ? 'bg-green-100 text-green-800'
                : invoice.status === 'pending'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {invoice.status === 'paid' ? 'Payée' : 
               invoice.status === 'pending' ? 'En attente' : 'Impayée'}
            </span>
          </div>
        </div>

        {/* Items Table */}
        <div className="mb-8">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b-2 border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Description</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Prix unitaire</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Quantité</th>
                <th className="text-right py-3 px-4 font-semibold text-gray-700">Total</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items.map((item) => (
                <tr key={item.id} className="border-b border-gray-100">
                  <td className="py-3 px-4 text-gray-900">{item.description}</td>
                  <td className="py-3 px-4 text-right text-gray-900">{formatCurrency(item.unitPrice)}</td>
                  <td className="py-3 px-4 text-right text-gray-900">{item.quantity}</td>
                  <td className="py-3 px-4 text-right text-gray-900 font-medium">{formatCurrency(item.total)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Totals */}
        <div className="flex justify-end">
          <div className="w-64 space-y-3">
            <div className="flex justify-between text-gray-600">
              <span>Sous-total:</span>
              <span>{formatCurrency(invoice.amount)}</span>
            </div>
            
            <div className="flex justify-between text-gray-600">
              <span>TVA ({invoice.taxRate}%):</span>
              <span>{formatCurrency(taxAmount)}</span>
            </div>
            
            <div className="flex justify-between text-lg font-bold text-gray-900 border-t border-gray-200 pt-2">
              <span>Total:</span>
              <span>{formatCurrency(totalAmount)}</span>
            </div>
          </div>
        </div>

        {/* Notes */}
        {invoice.notes && (
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">Notes</h4>
            <p className="text-gray-700">{invoice.notes}</p>
          </div>
        )}

        {/* Payment Instructions */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Instructions de paiement</h4>
          <p className="text-gray-700 text-sm">
            Cette facture a été réglée par carte bancaire. Conservez ce document pour vos archives.
            Pour toute question concernant cette facture, contactez-nous à support@uvda.com.
          </p>
        </div>
      </div>
    </div>
  );
};

export default InvoiceViewer;