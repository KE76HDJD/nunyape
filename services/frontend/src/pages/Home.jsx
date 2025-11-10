import React from 'react';
import { Link } from 'react-router-dom';
import { Play, Users, Zap, ArrowRight, Star } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <Play className="h-8 w-8" />,
      title: "Présentations Interactives",
      description: "Créez des présentations engageantes avec des éléments interactifs et des animations fluides."
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Collaboration en Temps Réel",
      description: "Travaillez ensemble avec votre équipe en temps réel sur les mêmes présentations."
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Performances Optimisées",
      description: "Des chargements ultra-rapides et une expérience utilisateur optimisée sur tous les appareils."
    }
  ];

  const testimonials = [
    {
      name: "Marie Lambert",
      role: "Responsable Marketing",
      company: "TechCorp",
      content: "UVDA a transformé notre façon de présenter. Les sessions de Q&A en direct sont incroyables !",
      rating: 5
    },
    {
      name: "Thomas Dubois",
      role: "Formateur",
      company: "EduPlus",
      content: "La plateforme parfaite pour mes formations en ligne. Mes étudiants adorent l'interactivité.",
      rating: 5
    },
    {
      name: "Sophie Martin",
      role: "Consultante",
      company: "InnovConsult",
      content: "Les outils de analytics m'aident à comprendre l'engagement de mon audience.",
      rating: 4
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Donnez vie à vos
              <span className="text-primary-600"> présentations</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              UVDA révolutionne les présentations avec des outils interactifs, 
              des sessions de Q&A en direct et une collaboration en temps réel.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Commencer gratuitement
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/presentation/create"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-primary-600 bg-white border border-primary-600 rounded-lg hover:bg-primary-50 transition-colors"
              >
                Voir une démo
              </Link>
            </div>
          </div>

          {/* Hero Image/Preview */}
          <div className="mt-16 bg-white rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
            <div className="aspect-video bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <div className="text-center text-white">
                <Play className="h-16 w-16 mx-auto mb-4" />
                <p className="text-xl">Aperçu de l'éditeur UVDA</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Pourquoi choisir UVDA ?
            </h2>
            <p className="text-xl text-gray-600">
              Des fonctionnalités conçues pour les présentations modernes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="text-center p-6 group hover:transform hover:-translate-y-2 transition-all duration-300"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 text-primary-600 rounded-lg mb-4 group-hover:bg-primary-600 group-hover:text-white transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Ils nous font confiance
            </h2>
            <p className="text-xl text-gray-600">
              Rejoignez des milliers de professionnels satisfaits
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-5 w-5 ${
                        i < testimonial.rating
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <p className="text-gray-700 mb-4 italic">
                  "{testimonial.content}"
                </p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold mr-3">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">
                      {testimonial.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      {testimonial.role}, {testimonial.company}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold text-white mb-4">
            Prêt à révolutionner vos présentations ?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Rejoignez UVDA aujourd'hui et découvrez une nouvelle façon de présenter
          </p>
          <Link
            to="/register"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-primary-600 bg-white rounded-lg hover:bg-gray-100 transition-colors"
          >
            Créer un compte gratuit
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;