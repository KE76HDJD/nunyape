import unittest
import sys
import os
from datetime import datetime, timedelta

# Ajout du chemin de l'application
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_auth_app, db
from app.models import User, RefreshToken

class TestAuthEndpoints(unittest.TestCase):
    """
    Tests d'intégration pour les endpoints d'authentification
    """
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = create_auth_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_health_check(self):
        """Test l'endpoint de santé"""
        response = self.client.get('/api/v1/auth/health')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'auth-service')
    
    def test_register_success(self):
        """Test l'enregistrement réussi d'un utilisateur"""
        user_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.post('/api/v1/auth/register', json=user_data)
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['email'], user_data['email'])
        self.assertEqual(data['user']['first_name'], user_data['first_name'])
    
    def test_register_duplicate_email(self):
        """Test l'enregistrement avec un email existant"""
        user_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        # Premier enregistrement
        self.client.post('/api/v1/auth/register', json=user_data)
        
        # Deuxième enregistrement avec le même email
        response = self.client.post('/api/v1/auth/register', json=user_data)
        
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn('existe déjà', data['error'])
    
    def test_register_missing_fields(self):
        """Test l'enregistrement avec des champs manquants"""
        user_data = {
            'email': 'test@example.com'
            # Champs manquants: password, first_name, last_name
        }
        
        response = self.client.post('/api/v1/auth/register', json=user_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Champ obligatoire manquant', data['error'])
    
    def test_login_success(self):
        """Test la connexion réussie"""
        # D'abord, enregistrer un utilisateur
        user_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        self.client.post('/api/v1/auth/register', json=user_data)
        
        # Puis tenter de se connecter
        login_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post('/api/v1/auth/login', json=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertEqual(data['user']['email'], login_data['email'])
    
    def test_login_invalid_credentials(self):
        """Test la connexion avec des identifiants invalides"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/v1/auth/login', json=login_data)
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('incorrect', data['error'])
    
    def test_login_missing_credentials(self):
        """Test la connexion avec des identifiants manquants"""
        login_data = {
            'email': 'test@example.com'
            # Mot de passe manquant
        }
        
        response = self.client.post('/api/v1/auth/login', json=login_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('requis', data['error'])

class TestUserModel(unittest.TestCase):
    """
    Tests unitaires pour le modèle User
    """
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = create_auth_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_creation(self):
        """Test la création d'un utilisateur"""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        user.set_password('SecurePass123!')
        
        with self.app.app_context():
            db.session.add(user)
            db.session.commit()
            
            # Vérification
            saved_user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.first_name, 'John')
            self.assertEqual(saved_user.last_name, 'Doe')
            self.assertTrue(saved_user.check_password('SecurePass123!'))
    
    def test_password_hashing(self):
        """Test le hachage et la vérification des mots de passe"""
        user = User(email='test@example.com')
        user.set_password('my_password')
        
        # Le hash ne doit pas être le mot de passe en clair
        self.assertNotEqual(user.password_hash, 'my_password')
        
        # La vérification doit fonctionner
        self.assertTrue(user.check_password('my_password'))
        self.assertFalse(user.check_password('wrong_password'))
    
    def test_user_to_dict(self):
        """Test la conversion de l'utilisateur en dictionnaire"""
        user = User(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            phone_number='+1234567890'
        )
        user.set_password('SecurePass123!')
        
        user_dict = user.to_dict()
        
        # Vérifie que le dictionnaire contient les bonnes clés
        expected_keys = ['id', 'email', 'first_name', 'last_name', 'phone_number', 
                        'is_active', 'is_verified', 'created_at', 'last_login']
        
        for key in expected_keys:
            self.assertIn(key, user_dict)
        
        # Vérifie que le mot de passe n'est pas inclus
        self.assertNotIn('password', user_dict)
        self.assertNotIn('password_hash', user_dict)

if __name__ == '__main__':
    unittest.main()