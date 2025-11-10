import React, { useState, useEffect } from 'react';
import { Save, Eye, Download, Plus, Trash2 } from 'lucide-react';
import SlideManager from './SlideManager';
import { uvdaApi } from '../../../services/uvda/api';

const PresentationEditor = () => {
  const [presentation, setPresentation] = useState({
    title: '',
    description: '',
    slides: [],
    theme: 'default',
    isPublic: false
  });
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Charger la présentation si on est en mode édition
    const loadPresentation = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const presentationId = urlParams.get('id');
      
      if (presentationId) {
        try {
          const data = await uvdaApi.getPresentation(presentationId);
          setPresentation(data);
        } catch (error) {
          console.error('Erreur lors du chargement:', error);
        }
      }
    };

    loadPresentation();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (presentation.id) {
        await uvdaApi.updatePresentation(presentation.id, presentation);
      } else {
        await uvdaApi.createPresentation(presentation);
      }
      // Afficher un message de succès
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const addSlide = () => {
    const newSlide = {
      id: Date.now(),
      title: `Slide ${presentation.slides.length + 1}`,
      content: '',
      layout: 'default',
      media: []
    };
    setPresentation(prev => ({
      ...prev,
      slides: [...prev.slides, newSlide]
    }));
    setCurrentSlide(presentation.slides.length);
  };

  const updateSlide = (slideIndex, updates) => {
    setPresentation(prev => ({
      ...prev,
      slides: prev.slides.map((slide, index) =>
        index === slideIndex ? { ...slide, ...updates } : slide
      )
    }));
  };

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <input
              type="text"
              value={presentation.title}
              onChange={(e) => setPresentation(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Titre de la présentation"
              className="text-2xl font-bold border-none focus:outline-none focus:ring-0"
            />
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={addSlide}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>Nouvelle slide</span>
            </button>
            
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn-secondary flex items-center space-x-2"
            >
              <Save className="h-4 w-4" />
              <span>{isSaving ? 'Sauvegarde...' : 'Sauvegarder'}</span>
            </button>
            
            <button className="btn-primary flex items-center space-x-2">
              <Eye className="h-4 w-4" />
              <span>Prévisualiser</span>
            </button>
          </div>
        </div>
      </div>

      {/* Editor Content */}
      <div className="flex-1 flex">
        {/* Slide Manager */}
        <div className="w-80 border-r border-gray-200 bg-gray-50">
          <SlideManager
            slides={presentation.slides}
            currentSlide={currentSlide}
            onSlideSelect={setCurrentSlide}
            onSlideUpdate={updateSlide}
            onSlideAdd={addSlide}
          />
        </div>

        {/* Main Editor */}
        <div className="flex-1 p-6 bg-white">
          {presentation.slides.length > 0 ? (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-lg border border-gray-200 p-8">
                <input
                  type="text"
                  value={presentation.slides[currentSlide]?.title || ''}
                  onChange={(e) => updateSlide(currentSlide, { title: e.target.value })}
                  className="w-full text-2xl font-bold mb-4 border-none focus:outline-none focus:ring-0"
                  placeholder="Titre de la slide"
                />
                
                <textarea
                  value={presentation.slides[currentSlide]?.content || ''}
                  onChange={(e) => updateSlide(currentSlide, { content: e.target.value })}
                  className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  placeholder="Contenu de la slide..."
                />
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <Presentation className="h-24 w-24 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Commencez votre présentation
              </h3>
              <p className="text-gray-500 mb-6">
                Créez votre première slide pour démarrer
              </p>
              <button
                onClick={addSlide}
                className="btn-primary flex items-center space-x-2 mx-auto"
              >
                <Plus className="h-4 w-4" />
                <span>Créer la première slide</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PresentationEditor;