import React, { useState, useEffect } from 'react';
import { ThumbsUp, MessageCircle, TrendingUp, Filter } from 'lucide-react';
import QuestionForm from './QuestionForm';
import { uvdaApi } from '../../../services/uvda/api';

const QuestionList = () => {
  const [questions, setQuestions] = useState([]);
  const [filter, setFilter] = useState('popular'); // 'popular', 'recent', 'unanswered'
  const [isLoading, setIsLoading] = useState(true);

  const presentationId = window.location.pathname.split('/').pop();

  useEffect(() => {
    loadQuestions();
  }, [presentationId]);

  const loadQuestions = async () => {
    setIsLoading(true);
    try {
      const data = await uvdaApi.getQuestions(presentationId);
      setQuestions(data);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVote = async (questionId, voteType) => {
    try {
      await uvdaApi.voteQuestion(questionId, voteType);
      loadQuestions(); // Recharger les questions
    } catch (error) {
      console.error('Erreur lors du vote:', error);
    }
  };

  const filteredQuestions = questions.filter(question => {
    switch (filter) {
      case 'popular':
        return question.voteCount > 0;
      case 'unanswered':
        return !question.answered;
      default:
        return true;
    }
  }).sort((a, b) => {
    switch (filter) {
      case 'popular':
        return b.voteCount - a.voteCount;
      case 'recent':
        return new Date(b.createdAt) - new Date(a.createdAt);
      default:
        return new Date(b.createdAt) - new Date(a.createdAt);
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Chargement des questions...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Questions & Réponses</h1>
        <div className="flex items-center space-x-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="recent">Plus récentes</option>
            <option value="popular">Plus populaires</option>
            <option value="unanswered">Sans réponse</option>
          </select>
        </div>
      </div>

      {/* Question Form */}
      <QuestionForm 
        presentationId={presentationId} 
        onQuestionSubmitted={loadQuestions}
      />

      {/* Questions List */}
      <div className="space-y-4">
        {filteredQuestions.length === 0 ? (
          <div className="text-center py-12">
            <MessageCircle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Aucune question pour le moment
            </h3>
            <p className="text-gray-500">
              Soyez le premier à poser une question !
            </p>
          </div>
        ) : (
          filteredQuestions.map((question) => (
            <div
              key={question.id}
              className={`card ${
                question.answered ? 'border-green-200 bg-green-50' : ''
              }`}
            >
              <div className="flex space-x-4">
                {/* Votes */}
                <div className="flex flex-col items-center space-y-2">
                  <button
                    onClick={() => handleVote(question.id, 'up')}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <ThumbsUp className="h-4 w-4 text-gray-500 hover:text-green-500" />
                  </button>
                  
                  <span className="text-sm font-medium text-gray-700">
                    {question.voteCount}
                  </span>
                </div>

                {/* Question Content */}
                <div className="flex-1">
                  <p className="text-gray-900 mb-2">{question.content}</p>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span>
                        {question.isAnonymous ? 'Anonyme' : question.author?.name}
                      </span>
                      <span>
                        {new Date(question.createdAt).toLocaleDateString()}
                      </span>
                      {question.answered && (
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                          Répondu
                        </span>
                      )}
                    </div>
                    
                    {question.commentCount > 0 && (
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{question.commentCount}</span>
                      </div>
                    )}
                  </div>

                  {/* Réponses */}
                  {question.answers && question.answers.length > 0 && (
                    <div className="mt-4 pl-4 border-l-2 border-green-200">
                      {question.answers.map((answer) => (
                        <div key={answer.id} className="mb-3 last:mb-0">
                          <p className="text-gray-700">{answer.content}</p>
                          <div className="text-xs text-gray-500 mt-1">
                            Par {answer.author?.name} • {new Date(answer.createdAt).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default QuestionList;