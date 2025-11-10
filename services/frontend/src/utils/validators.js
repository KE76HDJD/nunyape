// Validators pour les formulaires et données

export const commonValidators = {
  // Validation email
  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) return 'L\'email est requis';
    if (!emailRegex.test(value)) return 'Format d\'email invalide';
    return null;
  },

  // Validation mot de passe
  password: (value) => {
    if (!value) return 'Le mot de passe est requis';
    if (value.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères';
    if (!/(?=.*[a-z])/.test(value)) return 'Le mot de passe doit contenir au moins une minuscule';
    if (!/(?=.*[A-Z])/.test(value)) return 'Le mot de passe doit contenir au moins une majuscule';
    if (!/(?=.*\d)/.test(value)) return 'Le mot de passe doit contenir au moins un chiffre';
    return null;
  },

  // Validation confirmation mot de passe
  confirmPassword: (password, confirmPassword) => {
    if (!confirmPassword) return 'Veuillez confirmer votre mot de passe';
    if (password !== confirmPassword) return 'Les mots de passe ne correspondent pas';
    return null;
  },

  // Validation requis
  required: (value, fieldName = 'Ce champ') => {
    if (!value || (typeof value === 'string' && !value.trim())) {
      return `${fieldName} est requis`;
    }
    return null;
  },

  // Validation longueur minimale
  minLength: (value, min, fieldName = 'Ce champ') => {
    if (value && value.length < min) {
      return `${fieldName} doit contenir au moins ${min} caractères`;
    }
    return null;
  },

  // Validation longueur maximale
  maxLength: (value, max, fieldName = 'Ce champ') => {
    if (value && value.length > max) {
      return `${fieldName} ne peut pas dépasser ${max} caractères`;
    }
    return null;
  }
};

export const numberValidators = {
  // Validation nombre
  number: (value) => {
    if (value && isNaN(Number(value))) {
      return 'Veuillez entrer un nombre valide';
    }
    return null;
  },

  // Validation entier positif
  positiveInteger: (value) => {
    const num = Number(value);
    if (isNaN(num)) return 'Veuillez entrer un nombre valide';
    if (!Number.isInteger(num)) return 'Veuillez entrer un nombre entier';
    if (num < 0) return 'Le nombre doit être positif';
    return null;
  },

  // Validation plage de nombres
  range: (value, min, max) => {
    const num = Number(value);
    if (isNaN(num)) return 'Veuillez entrer un nombre valide';
    if (num < min || num > max) {
      return `Le nombre doit être entre ${min} et ${max}`;
    }
    return null;
  }
};

export const dateValidators = {
  // Validation date future
  futureDate: (value) => {
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (date < today) {
      return 'La date doit être dans le futur';
    }
    return null;
  },

  // Validation date passée
  pastDate: (value) => {
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (date > today) {
      return 'La date doit être dans le passé';
    }
    return null;
  },

  // Validation âge minimum
  minAge: (value, minAge) => {
    const birthDate = new Date(value);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    if (age < minAge) {
      return `Vous devez avoir au moins ${minAge} ans`;
    }
    return null;
  }
};

export const fileValidators = {
  // Validation type de fichier
  fileType: (file, allowedTypes) => {
    if (!file) return null;
    
    if (!allowedTypes.includes(file.type)) {
      const types = allowedTypes.map(t => t.split('/')[1]).join(', ');
      return `Type de fichier non supporté. Formats acceptés: ${types}`;
    }
    return null;
  },

  // Validation taille de fichier
  fileSize: (file, maxSizeMB) => {
    if (!file) return null;
    
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `La taille du fichier ne doit pas dépasser ${maxSizeMB} MB`;
    }
    return null;
  },

  // Validation dimensions image
  imageDimensions: (file, maxWidth, maxHeight) => {
    return new Promise((resolve) => {
      if (!file || !file.type.startsWith('image/')) {
        resolve(null);
        return;
      }

      const img = new Image();
      img.onload = () => {
        if (img.width > maxWidth || img.height > maxHeight) {
          resolve(`Les dimensions de l'image ne doivent pas dépasser ${maxWidth}x${maxHeight} pixels`);
        } else {
          resolve(null);
        }
      };
      img.onerror = () => resolve('Erreur lors du chargement de l\'image');
      img.src = URL.createObjectURL(file);
    });
  }
};

export const paymentValidators = {
  // Validation numéro de carte
  creditCard: (value) => {
    const cleaned = value.replace(/\s/g, '');
    if (!/^\d+$/.test(cleaned)) return 'Numéro de carte invalide';
    
    // Algorithme de Luhn
    let sum = 0;
    let isEven = false;
    
    for (let i = cleaned.length - 1; i >= 0; i--) {
      let digit = parseInt(cleaned[i], 10);
      
      if (isEven) {
        digit *= 2;
        if (digit > 9) digit -= 9;
      }
      
      sum += digit;
      isEven = !isEven;
    }
    
    if (sum % 10 !== 0) return 'Numéro de carte invalide';
    return null;
  },

  // Validation date d'expiration
  expirationDate: (value) => {
    if (!value) return 'Date d\'expiration requise';
    
    const [month, year] = value.split('/');
    if (!month || !year) return 'Format invalide (MM/AA)';
    
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    
    const expMonth = parseInt(month, 10);
    const expYear = parseInt(year, 10);
    
    if (expMonth < 1 || expMonth > 12) return 'Mois invalide';
    if (expYear < currentYear || (expYear === currentYear && expMonth < currentMonth)) {
      return 'Carte expirée';
    }
    
    return null;
  },

  // Validation CVV
  cvv: (value) => {
    if (!value) return 'CVV requis';
    if (!/^\d{3,4}$/.test(value)) return 'CVV invalide';
    return null;
  }
};

// Fonction utilitaire pour valider un objet de données avec un schéma
export const validateSchema = (data, schema) => {
  const errors = {};
  
  Object.keys(schema).forEach(field => {
    const validators = Array.isArray(schema[field]) ? schema[field] : [schema[field]];
    
    for (const validator of validators) {
      const error = validator(data[field], data);
      if (error) {
        errors[field] = error;
        break;
      }
    }
  });
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Export par défaut pour une utilisation facile
export default {
  common: commonValidators,
  number: numberValidators,
  date: dateValidators,
  file: fileValidators,
  payment: paymentValidators,
  validateSchema
};