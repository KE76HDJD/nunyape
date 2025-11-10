import axios from 'axios';

// Configuration de base de l'API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = 30000; // 30 secondes

// Instance axios de base
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs globales
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    if (error.response?.status === 403) {
      // Permission refusée
      console.error('Permission refusée:', error.response.data);
    }
    
    if (error.code === 'ECONNABORTED') {
      console.error('Timeout de la requête API');
    }
    
    return Promise.reject(error);
  }
);

class UVDAApi {
  constructor() {
    this.client = apiClient;
  }

  // ==================== AUTHENTIFICATION ====================
  
  async login(credentials) {
    const response = await this.client.post('/auth/login', credentials);
    return response.data;
  }

  async register(userData) {
    const response = await this.client.post('/auth/register', userData);
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/auth/logout');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    return response.data;
  }

  async refreshToken() {
    const response = await this.client.post('/auth/refresh');
    if (response.data.token) {
      localStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async changePassword(passwordData) {
    const response = await this.client.post('/auth/change-password', passwordData);
    return response.data;
  }

  async requestPasswordReset(email) {
    const response = await this.client.post('/auth/forgot-password', { email });
    return response.data;
  }

  async resetPassword(token, newPassword) {
    const response = await this.client.post('/auth/reset-password', {
      token,
      password: newPassword
    });
    return response.data;
  }

  // ==================== UTILISATEURS ====================

  async getUsers(params = {}) {
    const response = await this.client.get('/users', { params });
    return response.data;
  }

  async getUser(userId) {
    const response = await this.client.get(`/users/${userId}`);
    return response.data;
  }

  async updateUserProfile(userId, profileData) {
    const response = await this.client.put(`/users/${userId}`, profileData);
    
    // Mettre à jour le localStorage si c'est l'utilisateur courant
    const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
    if (currentUser.id === userId) {
      localStorage.setItem('user', JSON.stringify({
        ...currentUser,
        ...profileData
      }));
    }
    
    return response.data;
  }

  async updateUserAvatar(userId, avatarFile) {
    const formData = new FormData();
    formData.append('avatar', avatarFile);
    
    const response = await this.client.post(`/users/${userId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteUser(userId) {
    const response = await this.client.delete(`/users/${userId}`);
    return response.data;
  }

  // ==================== PRÉSENTATIONS ====================

  async getPresentations(params = {}) {
    const response = await this.client.get('/presentations', { params });
    return response.data;
  }

  async getPresentation(presentationId) {
    const response = await this.client.get(`/presentations/${presentationId}`);
    return response.data;
  }

  async createPresentation(presentationData) {
    const response = await this.client.post('/presentations', presentationData);
    return response.data;
  }

  async updatePresentation(presentationId, updates) {
    const response = await this.client.put(`/presentations/${presentationId}`, updates);
    return response.data;
  }

  async deletePresentation(presentationId) {
    const response = await this.client.delete(`/presentations/${presentationId}`);
    return response.data;
  }

  async duplicatePresentation(presentationId) {
    const response = await this.client.post(`/presentations/${presentationId}/duplicate`);
    return response.data;
  }

  async publishPresentation(presentationId) {
    const response = await this.client.post(`/presentations/${presentationId}/publish`);
    return response.data;
  }

  async unpublishPresentation(presentationId) {
    const response = await this.client.post(`/presentations/${presentationId}/unpublish`);
    return response.data;
  }

  async sharePresentation(presentationId, settings) {
    const response = await this.client.post(`/presentations/${presentationId}/share`, settings);
    return response.data;
  }

  async getPresentationAnalytics(presentationId) {
    const response = await this.client.get(`/presentations/${presentationId}/analytics`);
    return response.data;
  }

  // ==================== SLIDES ====================

  async addSlide(presentationId, slideData) {
    const response = await this.client.post(`/presentations/${presentationId}/slides`, slideData);
    return response.data;
  }

  async updateSlide(presentationId, slideId, updates) {
    const response = await this.client.put(`/presentations/${presentationId}/slides/${slideId}`, updates);
    return response.data;
  }

  async deleteSlide(presentationId, slideId) {
    const response = await this.client.delete(`/presentations/${presentationId}/slides/${slideId}`);
    return response.data;
  }

  async reorderSlides(presentationId, slidesOrder) {
    const response = await this.client.put(`/presentations/${presentationId}/slides/reorder`, {
      order: slidesOrder
    });
    return response.data;
  }

  // ==================== QUESTIONS & RÉPONSES ====================

  async getQuestions(presentationId, params = {}) {
    const response = await this.client.get(`/presentations/${presentationId}/questions`, { params });
    return response.data;
  }

  async submitQuestion(presentationId, question) {
    const response = await this.client.post(`/presentations/${presentationId}/questions`, question);
    return response.data;
  }

  async voteQuestion(questionId, vote) {
    const response = await this.client.post(`/questions/${questionId}/vote`, { vote });
    return response.data;
  }

  async answerQuestion(questionId, answer) {
    const response = await this.client.post(`/questions/${questionId}/answer`, answer);
    return response.data;
  }

  async deleteQuestion(questionId) {
    const response = await this.client.delete(`/questions/${questionId}`);
    return response.data;
  }

  async getQuestionReplies(questionId) {
    const response = await this.client.get(`/questions/${questionId}/replies`);
    return response.data;
  }

  // ==================== PAIEMENTS ====================

  async createPaymentSession(presentationId) {
    const response = await this.client.post('/payments/session', { presentationId });
    return response.data;
  }

  async getPaymentStatus(sessionId) {
    const response = await this.client.get(`/payments/session/${sessionId}`);
    return response.data;
  }

  async createSubscription(planId) {
    const response = await this.client.post('/payments/subscriptions', { planId });
    return response.data;
  }

  async cancelSubscription(subscriptionId) {
    const response = await this.client.delete(`/payments/subscriptions/${subscriptionId}`);
    return response.data;
  }

  async getInvoices() {
    const response = await this.client.get('/payments/invoices');
    return response.data;
  }

  async getInvoice(invoiceId) {
    const response = await this.client.get(`/payments/invoices/${invoiceId}`);
    return response.data;
  }

  async addPaymentMethod(paymentMethodData) {
    const response = await this.client.post('/payments/methods', paymentMethodData);
    return response.data;
  }

  async getPaymentMethods() {
    const response = await this.client.get('/payments/methods');
    return response.data;
  }

  async removePaymentMethod(paymentMethodId) {
    const response = await this.client.delete(`/payments/methods/${paymentMethodId}`);
    return response.data;
  }

  async requestRefund(paymentIntentId, reason) {
    const response = await this.client.post('/payments/refunds', {
      paymentIntentId,
      reason
    });
    return response.data;
  }

  // ==================== MÉDIAS ====================

  async uploadMedia(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options.presentationId) {
      formData.append('presentationId', options.presentationId);
    }
    if (options.folder) {
      formData.append('folder', options.folder);
    }

    const response = await this.client.post('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (options.onProgress) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          options.onProgress(progress);
        }
      },
    });
    
    return response.data;
  }

  async getMedia(mediaId) {
    const response = await this.client.get(`/media/${mediaId}`);
    return response.data;
  }

  async deleteMedia(mediaId) {
    const response = await this.client.delete(`/media/${mediaId}`);
    return response.data;
  }

  async getMediaList(params = {}) {
    const response = await this.client.get('/media', { params });
    return response.data;
  }

  // ==================== PRÉSENTATIONS EN DIRECT ====================

  async startLivePresentation(presentationId) {
    const response = await this.client.post(`/live/presentations/${presentationId}/start`);
    return response.data;
  }

  async stopLivePresentation(presentationId) {
    const response = await this.client.post(`/live/presentations/${presentationId}/stop`);
    return response.data;
  }

  async getLivePresentationStatus(presentationId) {
    const response = await this.client.get(`/live/presentations/${presentationId}/status`);
    return response.data;
  }

  async getLiveParticipants(presentationId) {
    const response = await this.client.get(`/live/presentations/${presentationId}/participants`);
    return response.data;
  }

  // ==================== STATISTIQUES & ANALYTICS ====================

  async getDashboardStats() {
    const response = await this.client.get('/analytics/dashboard');
    return response.data;
  }

  async getPresentationStats(presentationId) {
    const response = await this.client.get(`/analytics/presentations/${presentationId}`);
    return response.data;
  }

  async getUserEngagement(userId, params = {}) {
    const response = await this.client.get(`/analytics/users/${userId}/engagement`, { params });
    return response.data;
  }

  // ==================== PARAMÈTRES & CONFIGURATION ====================

  async getSettings() {
    const response = await this.client.get('/settings');
    return response.data;
  }

  async updateSettings(settings) {
    const response = await this.client.put('/settings', settings);
    return response.data;
  }

  async getNotifications(params = {}) {
    const response = await this.client.get('/notifications', { params });
    return response.data;
  }

  async markNotificationAsRead(notificationId) {
    const response = await this.client.put(`/notifications/${notificationId}/read`);
    return response.data;
  }

  async markAllNotificationsAsRead() {
    const response = await this.client.put('/notifications/read-all');
    return response.data;
  }

  // ==================== UTILITAIRES ====================

  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Service indisponible');
    }
  }

  async getAppVersion() {
    const response = await this.client.get('/version');
    return response.data;
  }

  // Méthode générique pour les requêtes personnalisées
  async customRequest(config) {
    const response = await this.client.request(config);
    return response.data;
  }
}

// Instance unique de l'API
export const uvdaApi = new UVDAApi();

// Export des méthodes individuelles pour une utilisation plus ciblée
export const authAPI = {
  login: (credentials) => uvdaApi.login(credentials),
  register: (userData) => uvdaApi.register(userData),
  logout: () => uvdaApi.logout(),
  getCurrentUser: () => uvdaApi.getCurrentUser(),
  refreshToken: () => uvdaApi.refreshToken(),
};

export const presentationsAPI = {
  getAll: (params) => uvdaApi.getPresentations(params),
  getById: (id) => uvdaApi.getPresentation(id),
  create: (data) => uvdaApi.createPresentation(data),
  update: (id, updates) => uvdaApi.updatePresentation(id, updates),
  delete: (id) => uvdaApi.deletePresentation(id),
  duplicate: (id) => uvdaApi.duplicatePresentation(id),
  publish: (id) => uvdaApi.publishPresentation(id),
  unpublish: (id) => uvdaApi.unpublishPresentation(id),
};

export const questionsAPI = {
  getByPresentation: (presentationId, params) => uvdaApi.getQuestions(presentationId, params),
  submit: (presentationId, question) => uvdaApi.submitQuestion(presentationId, question),
  vote: (questionId, vote) => uvdaApi.voteQuestion(questionId, vote),
  answer: (questionId, answer) => uvdaApi.answerQuestion(questionId, answer),
};

export const mediaAPI = {
  upload: (file, options) => uvdaApi.uploadMedia(file, options),
  get: (id) => uvdaApi.getMedia(id),
  delete: (id) => uvdaApi.deleteMedia(id),
  list: (params) => uvdaApi.getMediaList(params),
};

export const paymentAPI = {
  createSession: (presentationId) => uvdaApi.createPaymentSession(presentationId),
  getStatus: (sessionId) => uvdaApi.getPaymentStatus(sessionId),
  getInvoices: () => uvdaApi.getInvoices(),
  getInvoice: (id) => uvdaApi.getInvoice(id),
};

export default uvdaApi;