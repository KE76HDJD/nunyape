import { uvdaApi } from './api';

export const paymentService = {
  async createPaymentSession(presentationId) {
    try {
      const response = await uvdaApi.createPaymentSession(presentationId);
      return response;
    } catch (error) {
      console.error('Erreur création session paiement:', error);
      throw error;
    }
  },

  async getPaymentStatus(sessionId) {
    try {
      const response = await uvdaApi.getPaymentStatus(sessionId);
      return response;
    } catch (error) {
      console.error('Erreur statut paiement:', error);
      throw error;
    }
  },

  async createSubscription(planId) {
    try {
      const response = await uvdaApi.createSubscription(planId);
      return response;
    } catch (error) {
      console.error('Erreur création abonnement:', error);
      throw error;
    }
  },

  async cancelSubscription(subscriptionId) {
    try {
      const response = await uvdaApi.cancelSubscription(subscriptionId);
      return response;
    } catch (error) {
      console.error('Erreur annulation abonnement:', error);
      throw error;
    }
  },

  async getInvoices() {
    try {
      const response = await uvdaApi.getInvoices();
      return response;
    } catch (error) {
      console.error('Erreur récupération factures:', error);
      throw error;
    }
  },

  async getInvoice(invoiceId) {
    try {
      const response = await uvdaApi.getInvoice(invoiceId);
      return response;
    } catch (error) {
      console.error('Erreur récupération facture:', error);
      throw error;
    }
  },

  // Méthodes pour gérer les cartes de crédit
  async addPaymentMethod(paymentMethodData) {
    try {
      const response = await uvdaApi.addPaymentMethod(paymentMethodData);
      return response;
    } catch (error) {
      console.error('Erreur ajout moyen paiement:', error);
      throw error;
    }
  },

  async getPaymentMethods() {
    try {
      const response = await uvdaApi.getPaymentMethods();
      return response;
    } catch (error) {
      console.error('Erreur récupération moyens paiement:', error);
      throw error;
    }
  },

  async removePaymentMethod(paymentMethodId) {
    try {
      const response = await uvdaApi.removePaymentMethod(paymentMethodId);
      return response;
    } catch (error) {
      console.error('Erreur suppression moyen paiement:', error);
      throw error;
    }
  },

  // Méthodes pour les remboursements
  async requestRefund(paymentIntentId, reason) {
    try {
      const response = await uvdaApi.requestRefund(paymentIntentId, reason);
      return response;
    } catch (error) {
      console.error('Erreur demande remboursement:', error);
      throw error;
    }
  }
};