import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Fullscreen, Share2 } from 'lucide-react';
import { uvdaApi } from '../../../services/uvda/api';

const PresentationViewer = () => {
  const [presentation, setPresentation] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const loadPresentation = async () => {
      const presentationId = window.location.pathname.split('/').pop();
      try {
        const data = await uvdaApi.getPresentation(presentationId);
        setPresentation(data);
      } catch (error) {
        console.error('Erreur lors du chargement:', error);
      }
    };

    loadPresentation();
  }, []);

  const nextSlide = () => {
    if (presentation && currentSlide < presentation.slides.length - 1) {
      setCurrentSlide(prev => prev + 1);
    }
  };

  const prevSlide = () => {
    if (currentSlide > 0) {
      setCurrentSlide(prev => prev - 1);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  if (!presentation) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Chargement...</div>
      </div>
    );
  }

  const currentSlideData = presentation.slides[currentSlide];

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Presentation Header */}
      <div className="bg-black bg-opacity-50 text-white p-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{presentation.title}</h1>
          <p className="text-sm text-gray-300">
            Slide {currentSlide + 1} sur {presentation.slides.length}
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleFullscreen}
            className="p-2 hover:bg-white hover:bg-opacity-10 rounded transition-colors"
          >
            <Fullscreen className="h-5 w-5" />
          </button>
          
          <button className="p-2 hover:bg-white hover:bg-opacity-10 rounded transition-colors">
            <Share2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Slide Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-full max-h-[80vh] p-12">
          {currentSlideData ? (
            <div className="h-full flex flex-col">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">
                {currentSlideData.title}
              </h2>
              
              <div className="flex-1 prose prose-lg max-w-none">
                {currentSlideData.content && (
                  <div 
                    className="text-gray-700 text-xl leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: currentSlideData.content }}
                  />
                )}
                
                {currentSlideData.media && currentSlideData.media.length > 0 && (
                  <div className="mt-6 grid grid-cols-2 gap-4">
                    {currentSlideData.media.map((media, index) => (
                      <img
                        key={index}
                        src={media.url}
                        alt={media.alt}
                        className="rounded-lg shadow-md"
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500">
              Aucune slide disponible
            </div>
          )}
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="bg-black bg-opacity-50 text-white p-4 flex items-center justify-between">
        <button
          onClick={prevSlide}
          disabled={currentSlide === 0}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white bg-opacity-10 hover:bg-opacity-20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <ChevronLeft className="h-5 w-5" />
          <span>Précédent</span>
        </button>

        <div className="flex space-x-2">
          {presentation.slides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-3 h-3 rounded-full transition-all ${
                index === currentSlide 
                  ? 'bg-white' 
                  : 'bg-white bg-opacity-30 hover:bg-opacity-50'
              }`}
            />
          ))}
        </div>

        <button
          onClick={nextSlide}
          disabled={currentSlide === presentation.slides.length - 1}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white bg-opacity-10 hover:bg-opacity-20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          <span>Suivant</span>
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

export default PresentationViewer;