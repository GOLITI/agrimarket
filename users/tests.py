# users/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAPITestCase(APITestCase):
    """Tests des endpoints de l'application users."""

    def setUp(self):
        """Création des utilisateurs de test et de leurs tokens."""

        # Client normal
        self.client_user = User.objects.create_user(
            username='Kouadio225',
            email='kouadio225@gmail.com',
            password='testpass123',
            role='client',
            first_name='Konan',
            last_name='Kouadio',
            ville='Abidjan',
            telephone='0758745246'
        )

        # Producteur
        self.producteur_user = User.objects.create_user(
            username='Kone225',
            email='kone225@gmail.com',
            password='testpass123',
            role='producteur',
            first_name='Kone',
            last_name='Abdoulaye',
            ville='Sinfra',
            telephone='0506457852'
        )

        # Administrateur
        self.admin_user = User.objects.create_superuser(
            username='admin1',
            email='admin1@gmail.com',
            password='adminpass123',
            role='admin'
        )

        # Tokens JWT
        self.client_token = str(RefreshToken.for_user(self.client_user).access_token)
        self.producteur_token = str(RefreshToken.for_user(self.producteur_user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

    # ----------------------------------------------------
    # Helper pour authentification
    # ----------------------------------------------------

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ----------------------------------------------------
    # INSCRIPTION
    # ----------------------------------------------------

    def test_register_success(self):
        url = reverse('register')
        data = {
            'username': 'fofana',
            'email': 'fofana@gmail.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'role': 'client',
            'first_name': 'Fofana',
            'last_name': 'Moussa',
            'ville': 'Korhogo',
            'telephone': '0100547896'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'fofana')
        self.assertEqual(User.objects.count(), 4)

    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'fofana',
            'email': 'fofana@gmail.com',
            'password': 'newpass123',
            'password2': 'wrongpass',
            'role': 'client',
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    # ----------------------------------------------------
    # AUTHENTIFICATION JWT
    # ----------------------------------------------------

    def test_login_success(self):
        url = reverse('login')
        data = {'username': 'Kouadio225', 'password': 'testpass123'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {'username': 'Kouadio225', 'password': 'wrongpass'}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify(self):
        url = reverse('verify')

        response = self.client.post(url, {'token': self.client_token}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        url = reverse('refresh')
        refresh = RefreshToken.for_user(self.client_user)

        response = self.client.post(url, {'refresh': str(refresh)}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_blacklist(self):
        url = reverse('logout')
        refresh = RefreshToken.for_user(self.client_user)

        response = self.client.post(url, {'refresh': str(refresh)}, format='json')

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT])

    # ----------------------------------------------------
    # PROFIL CONNECTÉ (/me/)
    # ----------------------------------------------------

    def test_get_me_authenticated(self):
        self.authenticate(self.client_token)

        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'Kouadio225')
        self.assertIn('email', response.data)

    def test_get_me_unauthenticated(self):
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_me(self):
        self.authenticate(self.client_token)

        url = reverse('me')
        data = {'ville': 'Mopti', 'bio': 'Nouvelle bio'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ville'], 'Mopti')
        self.assertEqual(response.data['bio'], 'Nouvelle bio')

        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.ville, 'Mopti')

    def test_delete_me(self):
        self.authenticate(self.client_token)

        url = reverse('me')
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username='Kouadio225').exists())

    # ----------------------------------------------------
    # ADMIN : LISTE UTILISATEURS
    # ----------------------------------------------------

    def test_admin_list_filter_by_role(self):
        self.authenticate(self.admin_token)

        url = reverse('user-list')
        response = self.client.get(url, {'role': 'producteur'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'],
                         self.producteur_user.username)

    def test_admin_list_search(self):
        self.authenticate(self.admin_token)

        url = reverse('user-list')
        response = self.client.get(url, {'search': 'Kone'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'],
                         self.producteur_user.username)

    def test_client_cannot_access_admin_list(self):
        self.authenticate(self.client_token)

        url = reverse('user-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----------------------------------------------------
    # ADMIN : DÉTAIL UTILISATEUR
    # ----------------------------------------------------

    def test_admin_detail_user(self):
        self.authenticate(self.admin_token)

        url = reverse('user-detail', args=[self.producteur_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'],
                         self.producteur_user.username)
        self.assertIn('email', response.data)

    def test_client_cannot_access_admin_detail(self):
        self.authenticate(self.client_token)

        url = reverse('user-detail', args=[self.producteur_user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)