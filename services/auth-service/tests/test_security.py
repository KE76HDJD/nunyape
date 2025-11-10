import unittest
import sys
import os

# Ajout du chemin de l'application
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.security import (
    validate_email, 
    validate_password, 
    generate_secure_token,
    check_password_strength,
    sanitize_input
)

class TestSecurityFunctions(unittest.TestCase):
    """
    Tests unitaires pour les fonctions de sécurité
    """
    
    def test_validate_email_valid(self):
        """Test la validation d'emails valides"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(validate_email(email))
    
    def test_validate_email_invalid(self):
        """Test la validation d'emails invalides"""
        invalid_emails = [
            'invalid',
            'missing@domain',
            '@domain.com',
            'spaces in@email.com'
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(validate_email(email))
    
    def test_validate_password_strong(self):
        """Test la validation de mots de passe forts"""
        strong_password = "SecurePass123!"
        result = validate_password(strong_password)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_password_weak(self):
        """Test la validation de mots de passe faibles"""
        weak_passwords = [
            'short',           # Trop court
            'nouppercase123',  # Pas de majuscule
            'NOLOWERCASE123',  # Pas de minuscule
            'NoNumbers!',      # Pas de chiffres
            'NoSpecial123'     # Pas de caractères spéciaux
        ]
        
        for password in weak_passwords:
            with self.subTest(password=password):
                result = validate_password(password)
                self.assertFalse(result['valid'])
                self.assertGreater(len(result['errors']), 0)
    
    def test_generate_secure_token(self):
        """Test la génération de tokens sécurisés"""
        token1 = generate_secure_token()
        token2 = generate_secure_token()
        
        # Vérifie la longueur
        self.assertEqual(len(token1), 32)
        
        # Vérifie l'unicité
        self.assertNotEqual(token1, token2)
        
        # Vérifie le type
        self.assertIsInstance(token1, str)
    
    def test_check_password_strength(self):
        """Test l'évaluation de la force des mots de passe"""
        test_cases = [
            ('weak', 'abc', 0, 'Faible'),
            ('medium', 'MediumPass1', 4, 'Moyen'),
            ('strong', 'VeryStrongPass123!', 6, 'Fort')
        ]
        
        for name, password, expected_score, expected_strength in test_cases:
            with self.subTest(name=name):
                result = check_password_strength(password)
                self.assertEqual(result['score'], expected_score)
                self.assertEqual(result['strength'], expected_strength)
    
    def test_sanitize_input(self):
        """Test le nettoyage des entrées utilisateur"""
        test_cases = [
            ('<script>alert("xss")</script>', 'alert("xss")'),
            ("'; DROP TABLE users;--", ' DROP TABLE users'),
            ('normal input', 'normal input'),
            ('', ''),
            (None, '')
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = sanitize_input(input_str)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()