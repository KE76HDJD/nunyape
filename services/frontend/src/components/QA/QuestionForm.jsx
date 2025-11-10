import React, { useState } from 'react';
import { Send, Anonymous } from 'lucide-react';
import { uvdaApi } from '../../../services/uvda/api';

const QuestionForm = ({ presentationId, onQuestionSubmitted }) => {
  const [question, setQuestion] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) return;

    setIsSubmitting(true);
    try {
      await uvdaApi.submitQuestion(presentationId, {
        content: question.trim(),
        isAnonymous
      });
      
      setQuestion('');
      if (onQuestionSubmitted) {
        onQuestionSubmitted();
      }
    } catch (error) {
      console.error('Erreur lors de la soumission:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Poser une question
      </h3>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Quelle est votre question ?"
            className="input-field h-24 resize-none"
            disabled={isSubmitting}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isAnonymous}
              onChange={(e) => setIsAnonymous(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <Anonymous className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">Poser anonymement</span>
          </label>
          
          <button
            type="submit"
            disabled={!question.trim() || isSubmitting}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
            <span>{isSubmitting ? 'Envoi...' : 'Envoyer'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default QuestionForm;