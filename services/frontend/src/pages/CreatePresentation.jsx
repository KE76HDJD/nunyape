import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Eye, Settings } from 'lucide-react';
import PresentationEditor from '../components/presentation/PresentationEditor';
import { uvdaApi } from '../services/api';

const CreatePresentation = () => {
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = async (presentationData) => {
    setIsCreating(true);
    try {
      const presentation = await uvdaApi.createPresentation(presentationData);
      navigate(`/presentation/${presentation.id}/edit`);
    } catch (error) {
      console.error('Erreur lors de la création:', error);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Retour</span>
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Nouvelle présentation
              </h1>
              <p className="text-gray-600">
                Créez une présentation engageante en quelques minutes
              </p>
            </div>
          </div>
        </div>

        {/* Creation Form */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <PresentationCreationForm 
            onCreate={handleCreate}
            isCreating={isCreating}
          />
        </div>

        {/* Templates Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Ou choisir un template
          </h2>
          <TemplateGrid onTemplateSelect={handleCreate} />
        </div>
      </div>
    </div>
  );
};

const PresentationCreationForm = ({ onCreate, isCreating }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    template: 'blank',
    category: 'general',
    isPublic: false
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Titre de la présentation *
        </label>
        <input
          type="text"
          required
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Donnez un titre à votre présentation..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-lg"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Décrivez le contenu de votre présentation..."
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
        />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Catégorie
          </label>
          <select
            value={formData.category}
            onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="general">Général</option>
            <option value="business">Business</option>
            <option value="education">Éducation</option>
            <option value="marketing">Marketing</option>
            <option value="technology">Technologie</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Template de base
          </label>
          <select
            value={formData.template}
            onChange={(e) => setFormData(prev => ({ ...prev, template: e.target.value }))}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="blank">Vide</option>
            <option value="professional">Professionnel</option>
            <option value="creative">Créatif</option>
            <option value="minimal">Minimaliste</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between pt-6 border-t border-gray-200">
        <label className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={formData.isPublic}
            onChange={(e) => setFormData(prev => ({ ...prev, isPublic: e.target.checked }))}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-gray-700">
            Rendre cette présentation publique
          </span>
        </label>

        <button
          type="submit"
          disabled={!formData.title.trim() || isCreating}
          className="flex items-center space-x-2 px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Save className="h-5 w-5" />
          <span>{isCreating ? 'Création...' : 'Créer la présentation'}</span>
        </button>
      </div>
    </form>
  );
};

const TemplateGrid = ({ onTemplateSelect }) => {
  const templates = [
    {
      id: 'professional',
      name: 'Professionnel',
      description: 'Template élégant pour les présentations d\'entreprise',
      color: 'from-blue-500 to-blue-600',
      category: 'business'
    },
    {
      id: 'creative',
      name: 'Créatif',
      description: 'Design moderne avec des éléments créatifs',
      color: 'from-purple-500 to-pink-500',
      category: 'marketing'
    },
    {
      id: 'minimal',
      name: 'Minimaliste',
      description: 'Design épuré et efficace',
      color: 'from-gray-600 to-gray-700',
      category: 'general'
    },
    {
      id: 'education',
      name: 'Éducatif',
      description: 'Parfait pour les formations et cours',
      color: 'from-green-500 to-green-600',
      category: 'education'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {templates.map((template) => (
        <button
          key={template.id}
          onClick={() => onTemplateSelect({
            title: `Présentation ${template.name}`,
            description: template.description,
            template: template.id,
            category: template.category
          })}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-left hover:shadow-md transition-shadow group"
        >
          <div className={`aspect-video rounded-lg mb-4 bg-gradient-to-r ${template.color} group-hover:opacity-90 transition-opacity`} />
          <h3 className="font-semibold text-gray-900 mb-2">{template.name}</h3>
          <p className="text-sm text-gray-600">{template.description}</p>
        </button>
      ))}
    </div>
  );
};

export default CreatePresentation;