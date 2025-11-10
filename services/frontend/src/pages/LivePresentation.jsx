import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Users, MessageCircle, Share2, Eye, Clock, QrCode } from 'lucide-react';
import useWebSocket from '../hooks/useWebSocket';
import { uvdaApi } from '../services/api';

const LivePresentation = () => {
  const { id } = useParams();
  const [presentation, setPresentation] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [participants, setParticipants] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const { sendMessage, lastMessage } = useWebSocket(
    `ws://localhost:8000/ws/presentation/${id}`,
    {
      onMessage: handleWebSocketMessage
    }
  );

  useEffect(() => {
    loadPresentation();
  }, [id]);

  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage);
    }
  }, [lastMessage]);

  function handleWebSocketMessage(message) {
    switch (message.type) {
      case 'slide_change':
        setCurrentSlide(message.data.slideIndex);
        break;
      case 'participant_joined':
        setParticipants(prev => [...prev, message.data]);
        break;
      case 'participant_left':
        setParticipants(prev => prev.filter(p => p.id !== message.data.id));
        break;
      case 'new_question':
        setQuestions(prev => [message.data, ...prev]);
        break;
      case 'question_upvoted':
        setQuestions(prev => prev.map(q =>
          q.id === message.data.questionId
            ? { ...q, votes: message.data.newVotes }
            : q
        ));
        break;
      default:
        break;
    }
  }

  const loadPresentation = async () => {
    try {
      const data = await uvdaApi.getPresentation(id);
      setPresentation(data);
      setCurrentSlide(0);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const changeSlide = (slideIndex) => {
    setCurrentSlide(slideIndex);
    sendMessage({
      type: 'slide_change',
      data: { slideIndex }
    });
  };

  const sharePresentation = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      alert('Lien copié dans le presse-papier !');
    } catch (err) {
      console.error('Erreur lors de la copie:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-500">Chargement de la présentation...</div>
      </div>
    );
  }

  if (!presentation) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-500">Présentation non trouvée</div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 flex">
      {/* Main Presentation Area */}
      <div className="flex-1 flex flex-col">
        {/* Presentation Header */}
        <div className="bg-black bg-opacity-50 text-white p-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">{presentation.title}</h1>
            <p className="text-sm text-gray-300">
              Présentation en direct • Slide {currentSlide + 1} sur {presentation.slides.length}
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm">
              <Users className="h-4 w-4" />
              <span>{participants.length} participants</span>
            </div>
            
            <button
              onClick={sharePresentation}
              className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-10 rounded-lg hover:bg-opacity-20 transition-colors"
            >
              <Share2 className="h-4 w-4" />
              <span>Partager</span>
            </button>
          </div>
        </div>

        {/* Slide Display */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl h-full max-h-[80vh] p-12 overflow-auto">
            {presentation.slides[currentSlide] && (
              <div className="h-full">
                <h2 className="text-4xl font-bold text-gray-900 mb-6">
                  {presentation.slides[currentSlide].title}
                </h2>
                
                <div className="prose prose-lg max-w-none">
                  {presentation.slides[currentSlide].content && (
                    <div 
                      className="text-gray-700 text-xl leading-relaxed"
                      dangerouslySetInnerHTML={{ 
                        __html: presentation.slides[currentSlide].content 
                      }}
                    />
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Slide Navigation */}
        <div className="bg-black bg-opacity-50 text-white p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => changeSlide(currentSlide - 1)}
              disabled={currentSlide === 0}
              className="px-4 py-2 bg-white bg-opacity-10 rounded-lg hover:bg-opacity-20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Précédent
            </button>

            <div className="flex space-x-2">
              {presentation.slides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => changeSlide(index)}
                  className={`w-3 h-3 rounded-full transition-all ${
                    index === currentSlide 
                      ? 'bg-white' 
                      : 'bg-white bg-opacity-30 hover:bg-opacity-50'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={() => changeSlide(currentSlide + 1)}
              disabled={currentSlide === presentation.slides.length - 1}
              className="px-4 py-2 bg-white bg-opacity-10 rounded-lg hover:bg-opacity-20 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Suivant
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-80 bg-gray-800 text-white flex flex-col">
        {/* Participants Panel */}
        <div className="p-4 border-b border-gray-700">
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>Participants ({participants.length})</span>
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {participants.map((participant) => (
              <div key={participant.id} className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>{participant.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Questions Panel */}
        <div className="flex-1 p-4 border-b border-gray-700 overflow-y-auto">
          <h3 className="font-semibold mb-3 flex items-center space-x-2">
            <MessageCircle className="h-4 w-4" />
            <span>Questions ({questions.length})</span>
          </h3>
          <div className="space-y-3">
            {questions.map((question) => (
              <div key={question.id} className="bg-gray-700 rounded-lg p-3">
                <p className="text-sm mb-2">{question.content}</p>
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>{question.author}</span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => sendMessage({
                        type: 'upvote_question',
                        data: { questionId: question.id }
                      })}
                      className="flex items-center space-x-1 hover:text-white transition-colors"
                    >
                      <span>↑</span>
                      <span>{question.votes || 0}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Stats */}
        <div className="p-4">
          <h3 className="font-semibold mb-3">Statistiques en direct</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Participants actifs</span>
              <span>{participants.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Questions posées</span>
              <span>{questions.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Temps écoulé</span>
              <span>25:18</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LivePresentation;