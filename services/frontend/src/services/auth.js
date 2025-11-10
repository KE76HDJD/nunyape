import { uvdaApi } from './api';

export const authService = {
  async login(credentials) {
    const response = await uvdaApi.login(credentials);
    
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },

  async register(userData) {
    const response = await uvdaApi.register(userData);
    
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated() {
    return !!localStorage.getItem('auth_token');
  },

  async refreshToken() {
    // Implémentation du refresh token
    try {
      const response = await uvdaApi.refreshToken();
      if (response.token) {
        localStorage.setItem('auth_token', response.token);
      }
      return response;
    } catch (error) {
      this.logout();
      throw error;
    }
  },

  async updateProfile(userId, profileData) {
    const response = await uvdaApi.updateUserProfile(userId, profileData);
    
    // Mettre à jour le user dans le localStorage
    const currentUser = this.getCurrentUser();
    if (currentUser && currentUser.id === userId) {
      localStorage.setItem('user', JSON.stringify({
        ...currentUser,
        ...profileData
      }));
    }
    
    return response;
  },

  async changePassword(passwordData) {
    return await uvdaApi.changePassword(passwordData);
  },

  async requestPasswordReset(email) {
    return await uvdaApi.requestPasswordReset(email);
  },

  async resetPassword(token, newPassword) {
    return await uvdaApi.resetPassword(token, newPassword);
  }
};