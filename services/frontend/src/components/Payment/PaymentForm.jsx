import React, { useState } from 'react';
import { CreditCard, Lock, CheckCircle } from 'lucide-react';
import { uvdaApi } from '../../../services/uvda/api';

const Payment = () => {
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const handlePayment = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    try {
      // Simuler un traitement de paiement
      const session = await uvdaApi.createPaymentSession('presentation-id');
      
      // En production, intégrer avec Stripe ou autre processeur
      setTimeout(() => {
        setPaymentSuccess(true);
        setIsProcessing(false);
      }, 2000);
      
    } catch (error) {
      console.error('Erreur de paiement:', error);
      setIsProcessing(false);
    }
  };

  if (paymentSuccess) {
    return (
      <div className="max-w-md mx-auto text-center py-12">
        <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Paiement Réussi !
        </h2>
        <p className="text-gray-600 mb-6">
          Votre présentation a été débloquée. Vous pouvez maintenant y accéder.
        </p>
        <button
          onClick={() => window.location.href = '/presentations'}
          className="btn-primary"
        >
          Voir mes présentations
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <CreditCard className="h-12 w-12 text-primary-500 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-gray-900">Paiement</h2>
          <p className="text-gray-600">Accédez à la présentation premium</p>
        </div>

        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-700">Présentation Premium</span>
            <span className="text-2xl font-bold text-primary-600">€19.99</span>
          </div>
        </div>

        <form onSubmit={handlePayment}>
          {/* Méthode de paiement */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Méthode de paiement
            </label>
            <div className="grid grid-cols-2 gap-3">
              {['card', 'paypal'].map((method) => (
                <button
                  key={method}
                  type="button"
                  onClick={() => setPaymentMethod(method)}
                  className={`p-3 border rounded-lg text-center transition-all ${
                    paymentMethod === method
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="text-sm font-medium capitalize">
                    {method === 'card' ? 'Carte' : 'PayPal'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {paymentMethod === 'card' && (
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Numéro de carte
                </label>
                <input
                  type="text"
                  placeholder="1234 5678 9012 3456"
                  className="input-field"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date d'expiration
                  </label>
                  <input
                    type="text"
                    placeholder="MM/AA"
                    className="input-field"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CVV
                  </label>
                  <input
                    type="text"
                    placeholder="123"
                    className="input-field"
                    required
                  />
                </div>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isProcessing}
            className="w-full btn-primary flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Traitement...</span>
              </>
            ) : (
              <>
                <Lock className="h-4 w-4" />
                <span>Payer €19.99</span>
              </>
            )}
          </button>
        </form>

        <div className="mt-4 text-center text-xs text-gray-500 flex items-center justify-center space-x-1">
          <Lock className="h-3 w-3" />
          <span>Paiement sécurisé SSL</span>
        </div>
      </div>
    </div>
  );
};

export default Payment;