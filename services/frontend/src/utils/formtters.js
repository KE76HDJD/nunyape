// Formatters pour les dates, nombres, devises, etc.

export const dateFormatters = {
  // Format date complète
  fullDate: (date) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  },

  // Format date courte
  shortDate: (date) => {
    return new Date(date).toLocaleDateString('fr-FR');
  },

  // Format date relative (il y a...)
  relativeTime: (date) => {
    const now = new Date();
    const target = new Date(date);
    const diffInSeconds = Math.floor((now - target) / 1000);

    if (diffInSeconds < 60) {
      return 'à l\'instant';
    }

    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
      return `il y a ${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''}`;
    }

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
      return `il y a ${diffInHours} heure${diffInHours > 1 ? 's' : ''}`;
    }

    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) {
      return `il y a ${diffInDays} jour${diffInDays > 1 ? 's' : ''}`;
    }

    const diffInMonths = Math.floor(diffInDays / 30);
    if (diffInMonths < 12) {
      return `il y a ${diffInMonths} mois`;
    }

    const diffInYears = Math.floor(diffInMonths / 12);
    return `il y a ${diffInYears} an${diffInYears > 1 ? 's' : ''}`;
  },

  // Format pour les inputs datetime-local
  toDateTimeLocal: (date) => {
    const d = new Date(date);
    return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 16);
  }
};

export const numberFormatters = {
  // Format nombre avec séparateurs
  formatNumber: (number) => {
    return new Intl.NumberFormat('fr-FR').format(number);
  },

  // Format pourcentage
  formatPercent: (number, decimals = 1) => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(number / 100);
  },

  // Format devise
  formatCurrency: (amount, currency = 'EUR') => {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: currency
    }).format(amount);
  },

  // Format bytes en format lisible
  formatBytes: (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  },

  // Format durée en minutes:secondes
  formatDuration: (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
};

export const textFormatters = {
  // Tronquer le texte avec ellipse
  truncate: (text, maxLength) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },

  // Capitaliser la première lettre
  capitalize: (text) => {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  },

  // Formater en titre (chaque mot capitalisé)
  titleCase: (text) => {
    return text.replace(/\w\S*/g, (txt) => {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  },

  // Formater un slug
  slugify: (text) => {
    return text
      .toLowerCase()
      .replace(/[^\w ]+/g, '')
      .replace(/ +/g, '-');
  },

  // Nettoyer le HTML
  stripHtml: (html) => {
    const tmp = document.createElement('DIV');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  }
};

export const validationFormatters = {
  // Formater un numéro de téléphone français
  formatPhone: (phone) => {
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$/);
    if (match) {
      return `+33 ${match[1]} ${match[2]} ${match[3]} ${match[4]} ${match[5]}`;
    }
    return phone;
  },

  // Formater un SIRET
  formatSiret: (siret) => {
    const cleaned = siret.replace(/\D/g, '');
    if (cleaned.length === 14) {
      return cleaned.replace(/(\d{3})(\d{3})(\d{3})(\d{5})/, '$1 $2 $3 $4');
    }
    return siret;
  }
};

// Export par défaut pour une utilisation facile
export default {
  date: dateFormatters,
  number: numberFormatters,
  text: textFormatters,
  validation: validationFormatters
};