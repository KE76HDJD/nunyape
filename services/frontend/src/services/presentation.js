import { uvdaApi } from './api';

export const presentationService = {
  async getAllPresentations(filters = {}) {
    try {
      const response = await uvdaApi.getPresentations(filters);
      return response;
    } catch (error) {
      console.error('Erreur récupération présentations:', error);
      throw error;
    }
  },

  async getPresentation(id) {
    try {
      const response = await uvdaApi.getPresentation(id);
      return response;
    } catch (error) {
      console.error('Erreur récupération présentation:', error);
      throw error;
    }
  },

  async createPresentation(presentationData) {
    try {
      const response = await uvdaApi.createPresentation(presentationData);
      return response;
    } catch (error) {
      console.error('Erreur création présentation:', error);
      throw error;
    }
  },

  async updatePresentation(id, updates) {
    try {
      const response = await uvdaApi.updatePresentation(id, updates);
      return response;
    } catch (error) {
      console.error('Erreur mise à jour présentation:', error);
      throw error;
    }
  },

  async deletePresentation(id) {
    try {
      const response = await uvdaApi.deletePresentation(id);
      return response;
    } catch (error) {
      console.error('Erreur suppression présentation:', error);
      throw error;
    }
  },

  async duplicatePresentation(id) {
    try {
      const presentation = await this.getPresentation(id);
      const duplicateData = {
        ...presentation,
        title: `${presentation.title} (Copie)`,
        id: undefined
      };
      return await this.createPresentation(duplicateData);
    } catch (error) {
      console.error('Erreur duplication présentation:', error);
      throw error;
    }
  },

  async publishPresentation(id) {
    try {
      const response = await uvdaApi.updatePresentation(id, { 
        status: 'published',
        publishedAt: new Date().toISOString()
      });
      return response;
    } catch (error) {
      console.error('Erreur publication présentation:', error);
      throw error;
    }
  },

  async unpublishPresentation(id) {
    try {
      const response = await uvdaApi.updatePresentation(id, { 
        status: 'draft' 
      });
      return response;
    } catch (error) {
      console.error('Erreur dépublication présentation:', error);
      throw error;
    }
  },

  async sharePresentation(id, settings) {
    try {
      const response = await uvdaApi.sharePresentation(id, settings);
      return response;
    } catch (error) {
      console.error('Erreur partage présentation:', error);
      throw error;
    }
  },

  async getPresentationAnalytics(id) {
    try {
      const response = await uvdaApi.getPresentationAnalytics(id);
      return response;
    } catch (error) {
      console.error('Erreur analytics présentation:', error);
      throw error;
    }
  },

  // Gestion des slides
  async addSlide(presentationId, slideData) {
    try {
      const response = await uvdaApi.addSlide(presentationId, slideData);
      return response;
    } catch (error) {
      console.error('Erreur ajout slide:', error);
      throw error;
    }
  },

  async updateSlide(presentationId, slideId, updates) {
    try {
      const response = await uvdaApi.updateSlide(presentationId, slideId, updates);
      return response;
    } catch (error) {
      console.error('Erreur mise à jour slide:', error);
      throw error;
    }
  },

  async deleteSlide(presentationId, slideId) {
    try {
      const response = await uvdaApi.deleteSlide(presentationId, slideId);
      return response;
    } catch (error) {
      console.error('Erreur suppression slide:', error);
      throw error;
    }
  },

  async reorderSlides(presentationId, slidesOrder) {
    try {
      const response = await uvdaApi.reorderSlides(presentationId, slidesOrder);
      return response;
    } catch (error) {
      console.error('Erreur réorganisation slides:', error);
      throw error;
    }
  }
};