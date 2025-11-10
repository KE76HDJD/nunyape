import React from 'react';
import { Heart } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span>&copy; 2024 UVDA Platform. Tous droits réservés.</span>
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <a href="#" className="hover:text-primary-600 transition-colors">Conditions d'utilisation</a>
            <a href="#" className="hover:text-primary-600 transition-colors">Politique de confidentialité</a>
            <a href="#" className="hover:text-primary-600 transition-colors">Support</a>
          </div>

          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <span>Made with</span>
            <Heart className="h-4 w-4 text-red-500" />
            <span>by UVDA Team</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;