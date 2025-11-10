import { useState, useEffect, useCallback } from 'react';
import { uvdaApi } from '../../services/uvda/api';

const usePresentation = (presentationId = null) => {
  const [presentation, setPresentation] = useState(null);
  const [presentations, setPresentations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Charger une présentation spécifique
  const loadPresentation = useCallback(async (id = presentationId) => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await uvdaApi.getPresentation(id);
      setPresentation(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors du chargement');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [presentationId]);

  // Charger toutes les présentations
  const loadPresentations = useCallback(async (filters = {}) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await uvdaApi.getPresentations(filters);
      setPresentations(data);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors du chargement');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Créer une nouvelle présentation
  const createPresentation = useCallback(async (presentationData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await uvdaApi.createPresentation(presentationData);
      setPresentations(prev => [data, ...prev]);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de la création');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Mettre à jour une présentation
  const updatePresentation = useCallback(async (id, updates) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await uvdaApi.updatePresentation(id, updates);
      
      // Mettre à jour la présentation courante
      if (presentation?.id === id) {
        setPresentation(data);
      }
      
      // Mettre à jour la liste des présentations
      setPresentations(prev => 
        prev.map(p => p.id === id ? data : p)
      );
      
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de la mise à jour');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [presentation]);

  // Supprimer une présentation
  const deletePresentation = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await uvdaApi.deletePresentation(id);
      
      // Retirer de la liste
      setPresentations(prev => prev.filter(p => p.id !== id));
      
      // Si c'est la présentation courante, la vider
      if (presentation?.id === id) {
        setPresentation(null);
      }
      
      return true;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de la suppression');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [presentation]);

  // Dupliquer une présentation
  const duplicatePresentation = useCallback(async (id) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const original = presentations.find(p => p.id === id);
      if (!original) throw new Error('Présentation non trouvée');
      
      const duplicateData = {
        ...original,
        title: `${original.title} (Copie)`,
        id: undefined,
        createdAt: undefined,
        updatedAt: undefined
      };
      
      const data = await uvdaApi.createPresentation(duplicateData);
      setPresentations(prev => [data, ...prev]);
      return data;
    } catch (err) {
      setError(err.response?.data?.message || 'Erreur lors de la duplication');
      console.error('Erreur:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [presentations]);

  // Publier/dépublier une présentation
  const togglePublish = useCallback(async (id, publish = true) => {
    return updatePresentation(id, { isPublished: publish });
  }, [updatePresentation]);

  // Recharger les données
  const refresh = useCallback(() => {
    if (presentationId) {
      loadPresentation(presentationId);
    } else {
      loadPresentations();
    }
  }, [presentationId, loadPresentation, loadPresentations]);

  // Effet pour charger automatiquement
  useEffect(() => {
    if (presentationId) {
      loadPresentation();
    } else {
      loadPresentations();
    }
  }, [presentationId, loadPresentation, loadPresentations]);

  return {
    // État
    presentation,
    presentations,
    isLoading,
    error,
    
    // Actions
    loadPresentation,
    loadPresentations,
    createPresentation,
    updatePresentation,
    deletePresentation,
    duplicatePresentation,
    togglePublish,
    refresh,
    
    // Utilitaires
    setError,
    clearError: () => setError(null)
  };
};

export default usePresentation;