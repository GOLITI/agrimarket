# products/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()

class ProductAPITestCase(APITestCase):
    """Tests pour l'application products."""

    def setUp(self):
        # Créer les utilisateurs
        self.client_user = User.objects.create_user(
            username='client1', password='pass123', role='client'
        )
        self.producteur_user = User.objects.create_user(
            username='prod1', password='pass123', role='producteur'
        )
        self.other_producteur = User.objects.create_user(
            username='prod2', password='pass123', role='producteur'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin', password='admin123', role='admin'
        )

        # Tokens
        self.client_token = self.get_token(self.client_user)
        self.producteur_token = self.get_token(self.producteur_user)
        self.other_producteur_token = self.get_token(self.other_producteur)
        self.admin_token = self.get_token(self.admin_user)

        # Créer des catégories
        self.cat1 = Category.objects.create(nom="Fruits", description="Fruits frais")
        self.cat2 = Category.objects.create(nom="Légumes", description="Légumes bio")

        # Créer des produits
        self.prod1 = Product.objects.create(
            nom="Mangue",
            description="Mangue mûre",
            prix=1000,
            stock=50,
            unite=Product.Unite.KG,
            producteur=self.producteur_user,
            disponible=True
        )
        self.prod1.categories.add(self.cat1)

        self.prod2 = Product.objects.create(
            nom="Tomate",
            description="Tomate cerise",
            prix=500,
            stock=0,
            unite=Product.Unite.KG,
            producteur=self.other_producteur,
            disponible=False
        )
        self.prod2.categories.add(self.cat2)

    def get_token(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    # ---------- CATÉGORIES ----------
    def test_list_categories_public(self):
        """Tout le monde peut lister les catégories."""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_category_admin_only(self):
        """Seul l'admin peut créer une catégorie."""
        url = reverse('category-list')
        data = {'nom': 'Céréales', 'description': 'Grains'}
        # Client normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Producteur
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)

    def test_update_category_admin_only(self):
        """Seul l'admin peut modifier une catégorie."""
        url = reverse('category-detail', args=[self.cat1.id])
        data = {'nom': 'Fruits exotiques'}
        # Client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.nom, 'Fruits exotiques')

    def test_delete_category_admin_only(self):
        """Seul l'admin peut supprimer une catégorie."""
        url = reverse('category-detail', args=[self.cat2.id])
        # Producteur
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.cat2.id).exists())

    # ---------- PRODUITS ----------
    def test_list_products_public(self):
        """Liste publique des produits."""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_product_public(self):
        """Détail public d'un produit."""
        url = reverse('product-detail', args=[self.prod1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nom'], 'Mangue')
        self.assertIn('producteur', response.data)
        self.assertEqual(response.data['producteur']['username'], 'prod1')

    def test_create_product_producteur_only(self):
        """Seul un producteur peut créer un produit."""
        url = reverse('product-list')
        data = {
            'nom': 'Banane',
            'description': 'Banane plantain',
            'prix': 800,
            'stock': 30,
            'unite': 'kg',
            'categorie_ids': [self.cat1.id],
            'disponible': True
        }
        # Client normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Producteur
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
        new_product = Product.objects.get(nom='Banane')
        self.assertEqual(new_product.producteur, self.producteur_user)
        self.assertEqual(new_product.categories.count(), 1)

    def test_producteur_modify_own_product(self):
        """Un producteur peut modifier son propre produit."""
        url = reverse('product-detail', args=[self.prod1.id])
        data = {'prix': 1200}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.prix, 1200)

    def test_producteur_cannot_modify_other_product(self):
        """Un producteur ne peut pas modifier le produit d'un autre."""
        url = reverse('product-detail', args=[self.prod1.id])  # prod1 appartient à producteur_user
        data = {'prix': 1200}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_producteur_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_modify_any_product(self):
        """L'admin peut modifier n'importe quel produit."""
        url = reverse('product-detail', args=[self.prod1.id])
        data = {'prix': 1500}
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.prix, 1500)

    def test_delete_product_owner_only(self):
        """Seul le propriétaire ou l'admin peut supprimer."""
        url = reverse('product-detail', args=[self.prod1.id])
        # Autre producteur
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_producteur_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Propriétaire
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.prod1.id).exists())

    # ---------- VALIDATIONS MÉTIER ----------
    def test_stock_cannot_be_negative(self):
        """Le stock ne peut pas être négatif."""
        url = reverse('product-list')
        data = {
            'nom': 'Test',
            'description': 'test',
            'prix': 100,
            'stock': -5,
            'unite': 'kg',
            'categorie_ids': [self.cat1.id],
            'disponible': True
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data)

    def test_prix_positive(self):
        """Le prix doit être positif."""
        url = reverse('product-list')
        data = {
            'nom': 'Test',
            'description': 'test',
            'prix': 0,
            'stock': 10,
            'unite': 'kg',
            'categorie_ids': [self.cat1.id],
            'disponible': True
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prix', response.data)

    def test_stock_zero_disponible_false(self):
        """Si stock=0, disponible doit être False."""
        url = reverse('product-list')
        data = {
            'nom': 'Test',
            'description': 'test',
            'prix': 100,
            'stock': 0,
            'unite': 'kg',
            'categorie_ids': [self.cat1.id],
            'disponible': True
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)  # validation croisée

    # ---------- FILTRES ----------
    def test_filter_by_categorie(self):
        """Filtrage par catégorie."""
        url = reverse('product-list')
        response = self.client.get(url, {'categories': self.cat1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nom'], 'Mangue')

    def test_filter_by_producteur(self):
        """Filtrage par producteur."""
        url = reverse('product-list')
        response = self.client.get(url, {'producteur': self.producteur_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nom'], 'Mangue')

    def test_filter_by_disponible(self):
        """Filtrage par disponibilité."""
        url = reverse('product-list')
        response = self.client.get(url, {'disponible': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nom'], 'Mangue')

    def test_search_by_nom(self):
        """Recherche par nom."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Mangue'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ordering_by_prix(self):
        """Tri par prix."""
        # Créer un autre produit pour tester le tri
        prod3 = Product.objects.create(
            nom='Ananas',
            description='Ananas frais',
            prix=2000,
            stock=10,
            producteur=self.producteur_user,
            disponible=True
        )
        url = reverse('product-list')
        response = self.client.get(url, {'ordering': 'prix'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(results[0]['prix'], '500.00')  # Tomate
        self.assertEqual(results[1]['prix'], '1000.00') # Mangue
        self.assertEqual(results[2]['prix'], '2000.00') # Ananas