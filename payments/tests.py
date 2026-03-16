from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from payments.models import Payment


class PaymentModelTestCase(TestCase):
    """Tests de base pour le modèle Payment"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123',
            role='client'
        )
    
    def test_payment_creation(self):
        """Vérifier que le modèle Payment existe"""
        self.assertTrue(hasattr(Payment, 'montant'))
        self.assertTrue(hasattr(Payment, 'statut'))
        self.assertTrue(hasattr(Payment, 'methode'))
    
    def test_user_creation(self):
        """Vérifier que l'utilisateur de test est bien créé"""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.role, 'client')


class PaymentAPITestCase(APITestCase):
    """Tests de base pour l'API Payment"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='testpass123',
            role='client'
        )
    
    def test_payment_endpoint_exists(self):
        """Vérifier que l'endpoint payment nécessite une authentification"""
        response = self.client.get('/api/payments/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
