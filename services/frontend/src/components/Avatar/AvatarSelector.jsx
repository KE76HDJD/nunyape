import React, { useState, useRef } from 'react';
import { Upload, Camera, User, Check, X } from 'lucide-react';
import Avatar from './Avatar';

const AvatarSelector = ({ currentAvatar, onAvatarChange, size = "xl" }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(currentAvatar);
  const [isEditing, setIsEditing] = useState(false);
  const fileInputRef = useRef(null);

  const defaultAvatars = [
    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&h=150&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&h=150&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
  ];

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        setIsEditing(true);
      } else {
        alert('Veuillez sélectionner une image valide');
      }
    }
  };

  const handleAvatarSelect = (avatarUrl) => {
    setPreviewUrl(avatarUrl);
    setSelectedFile(null);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (onAvatarChange) {
      onAvatarChange(previewUrl, selectedFile);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setPreviewUrl(currentAvatar);
    setSelectedFile(null);
    setIsEditing(false);
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="flex flex-col items-center space-y-6 p-6">
      {/* Current Avatar Preview */}
      <div className="relative">
        <Avatar 
          src={previewUrl} 
          size={size}
          className="border-4 border-white shadow-lg"
        />
        
        {/* Edit Overlay */}
        <button
          onClick={triggerFileInput}
          className="absolute -bottom-2 -right-2 bg-primary-600 text-white p-2 rounded-full shadow-lg hover:bg-primary-700 transition-colors"
        >
          <Camera className="h-4 w-4" />
        </button>

        {/* Editing Controls */}
        {isEditing && (
          <div className="absolute -bottom-2 -left-2 flex space-x-2">
            <button
              onClick={handleSave}
              className="bg-green-600 text-white p-2 rounded-full shadow-lg hover:bg-green-700 transition-colors"
            >
              <Check className="h-4 w-4" />
            </button>
            <button
              onClick={handleCancel}
              className="bg-red-600 text-white p-2 rounded-full shadow-lg hover:bg-red-700 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="image/*"
        className="hidden"
      />

      {/* Default Avatars */}
      <div className="w-full">
        <h3 className="text-sm font-medium text-gray-700 mb-3 text-center">
          Ou choisir un avatar par défaut
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {defaultAvatars.map((avatar, index) => (
            <button
              key={index}
              onClick={() => handleAvatarSelect(avatar)}
              className={`p-1 rounded-full transition-all ${
                previewUrl === avatar 
                  ? 'ring-2 ring-primary-500 ring-offset-2' 
                  : 'hover:scale-110'
              }`}
            >
              <Avatar 
                src={avatar} 
                size="md"
                className="shadow-md"
              />
            </button>
          ))}
        </div>
      </div>

      {/* Upload Button */}
      <button
        onClick={triggerFileInput}
        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
      >
        <Upload className="h-4 w-4" />
        <span>Télécharger une image</span>
      </button>

      {/* File Info */}
      {selectedFile && (
        <div className="text-center text-sm text-gray-600">
          <p>Fichier sélectionné: {selectedFile.name}</p>
          <p>Taille: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
      )}
    </div>
  );
};

export default AvatarSelector;