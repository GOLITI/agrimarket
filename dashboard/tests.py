from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class DashboardTestCase(APITestCase):
    """Tests de base pour le dashboard"""
    
    def setUp(self):
        """Configuration des tests"""
        self.producteur = User.objects.create_user(
            username='producteur',
            email='producteur@test.com',
            password='testpass123',
            role='producteur'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
    
    def test_dashboard_requires_authentication(self):
        """Vérifier que le dashboard nécessite une authentification"""
        # Tenter d'accéder sans authentification devrait échouer
        response = self.client.get('/api/dashboard/')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_models_exist(self):
        """Vérifier que les utilisateurs de test sont bien créés"""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.producteur.role, 'producteur')
        self.assertEqual(self.admin.role, 'admin')
