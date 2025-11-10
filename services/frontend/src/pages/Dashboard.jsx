import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Grid, List, Eye, Edit, MoreVertical } from 'lucide-react';
import { uvdaApi } from '../services/api';
import usePresentation from '../hooks/usePresentation';

const Dashboard = () => {
  const [viewMode, setViewMode] = useState('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const { presentations, loadPresentations, isLoading } = usePresentation();

  useEffect(() => {
    loadPresentations();
  }, []);

  const filteredPresentations = presentations.filter(presentation => {
    const matchesSearch = presentation.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || presentation.status === filter;
    return matchesSearch && matchesFilter;
  });

  const stats = {
    total: presentations.length,
    published: presentations.filter(p => p.status === 'published').length,
    draft: presentations.filter(p => p.status === 'draft').length,
    recent: presentations.filter(p => {
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
      return new Date(p.updatedAt) > oneWeekAgo;
    }).length
  };

  const PresentationCard = ({ presentation }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
      <div className="aspect-video bg-gradient-to-r from-blue-500 to-purple-600 rounded-t-xl relative">
        {presentation.thumbnail && (
          <img
            src={presentation.thumbnail}
            alt={presentation.title}
            className="w-full h-full object-cover rounded-t-xl"
          />
        )}
        <div className="absolute top-3 right-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            presentation.status === 'published' 
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {presentation.status === 'published' ? 'Publié' : 'Brouillon'}
          </span>
        </div>
      </div>
      
      <div className="p-4">
        <h3 className="font-semibold text-gray-900 mb-2 truncate">
          {presentation.title}
        </h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {presentation.description || 'Aucune description'}
        </p>
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>
            {new Date(presentation.updatedAt).toLocaleDateString('fr-FR')}
          </span>
          <span>
            {presentation.slidesCount || 0} slides
          </span>
        </div>
        
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <Link
              to={`/presentation/${presentation.id}/view`}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Eye className="h-4 w-4" />
            </Link>
            <Link
              to={`/presentation/${presentation.id}/edit`}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Edit className="h-4 w-4" />
            </Link>
          </div>
          
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );

  const PresentationListItem = ({ presentation }) => (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 flex-1">
          <div className="w-20 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex-shrink-0">
            {presentation.thumbnail && (
              <img
                src={presentation.thumbnail}
                alt={presentation.title}
                className="w-full h-full object-cover rounded-lg"
              />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 truncate">
              {presentation.title}
            </h3>
            <p className="text-gray-600 text-sm truncate">
              {presentation.description || 'Aucune description'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-6 text-sm text-gray-500">
          <span>
            {new Date(presentation.updatedAt).toLocaleDateString('fr-FR')}
          </span>
          <span>
            {presentation.slidesCount || 0} slides
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            presentation.status === 'published' 
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {presentation.status === 'published' ? 'Publié' : 'Brouillon'}
          </span>
        </div>
        
        <div className="flex items-center space-x-2 ml-6">
          <Link
            to={`/presentation/${presentation.id}/view`}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Eye className="h-4 w-4" />
          </Link>
          <Link
            to={`/presentation/${presentation.id}/edit`}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Edit className="h-4 w-4" />
          </Link>
          <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-500">Chargement...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600">Gérez vos présentations et analysez vos performances</p>
        </div>
        <Link
          to="/presentation/create"
          className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          <span>Nouvelle présentation</span>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-gray-600">Total présentations</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-green-600">{stats.published}</div>
          <div className="text-gray-600">Publiées</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-yellow-600">{stats.draft}</div>
          <div className="text-gray-600">Brouillons</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="text-2xl font-bold text-blue-600">{stats.recent}</div>
          <div className="text-gray-600">Récentes (7j)</div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-4 flex-1 max-w-md">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Rechercher une présentation..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">Tous</option>
              <option value="published">Publiées</option>
              <option value="draft">Brouillons</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg ${
                viewMode === 'grid'
                  ? 'bg-primary-100 text-primary-600'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <Grid className="h-5 w-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-lg ${
                viewMode === 'list'
                  ? 'bg-primary-100 text-primary-600'
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <List className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Presentations */}
      {filteredPresentations.length === 0 ? (
        <div className="text-center py-12">
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4">
            <Plus className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune présentation
          </h3>
          <p className="text-gray-600 mb-6">
            Commencez par créer votre première présentation
          </p>
          <Link
            to="/presentation/create"
            className="inline-flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="h-5 w-5" />
            <span>Créer une présentation</span>
          </Link>
        </div>
      ) : (
        <div className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
            : 'space-y-4'
        }>
          {filteredPresentations.map((presentation) =>
            viewMode === 'grid' ? (
              <PresentationCard
                key={presentation.id}
                presentation={presentation}
              />
            ) : (
              <PresentationListItem
                key={presentation.id}
                presentation={presentation}
              />
            )
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;