import React, { useState } from 'react';
import { ZoomIn, ZoomOut, Download, RotateCw } from 'lucide-react';
import Avatar from './Avatar';

const AvatarViewer = ({ 
  avatarUrl, 
  userName = "Utilisateur",
  role = "Membre",
  onEdit,
  showControls = true 
}) => {
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.1, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.1, 1));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const handleDownload = () => {
    if (avatarUrl) {
      const link = document.createElement('a');
      link.href = avatarUrl;
      link.download = `avatar-${userName.toLowerCase().replace(' ', '-')}.jpg`;
      link.click();
    }
  };

  const transformStyle = {
    transform: `scale(${zoom}) rotate(${rotation}deg)`,
    transition: 'transform 0.3s ease'
  };

  return (
    <div className="flex flex-col items-center space-y-6 p-6 bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Avatar Container */}
      <div className="relative">
        <div className="overflow-hidden rounded-full border-4 border-white shadow-xl">
          <div style={transformStyle}>
            <Avatar 
              src={avatarUrl} 
              size="2xl"
              className="transition-transform duration-300"
            />
          </div>
        </div>

        {/* Online Status Indicator */}
        <div className="absolute bottom-2 right-2">
          <div className="w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
        </div>
      </div>

      {/* User Info */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">{userName}</h2>
        <p className="text-gray-600">{role}</p>
      </div>

      {/* Controls */}
      {showControls && (
        <div className="flex flex-col space-y-4 w-full max-w-xs">
          {/* Zoom Controls */}
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-3">
            <span className="text-sm font-medium text-gray-700">Zoom</span>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleZoomOut}
                disabled={zoom <= 1}
                className="p-1 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              
              <span className="text-xs text-gray-500 w-8 text-center">
                {Math.round(zoom * 100)}%
              </span>
              
              <button
                onClick={handleZoomIn}
                disabled={zoom >= 3}
                className="p-1 text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={handleRotate}
              className="flex flex-col items-center space-y-1 p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RotateCw className="h-4 w-4" />
              <span className="text-xs">Tourner</span>
            </button>

            <button
              onClick={handleDownload}
              disabled={!avatarUrl}
              className="flex flex-col items-center space-y-1 p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              <span className="text-xs">Télécharger</span>
            </button>

            {onEdit && (
              <button
                onClick={onEdit}
                className="flex flex-col items-center space-y-1 p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span className="text-xs">Modifier</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Avatar Statistics */}
      <div className="w-full border-t border-gray-200 pt-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-gray-900">24</div>
            <div className="text-xs text-gray-500">Présentations</div>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-900">156</div>
            <div className="text-xs text-gray-500">Questions</div>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-900">89%</div>
            <div className="text-xs text-gray-500">Engagement</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarViewer;