# orders/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from products.models import Category, Product
from orders.models import Order, OrderItem
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class OrderAPITestCase(APITestCase):
    """Tests pour l'application orders."""

    def setUp(self):
        # Création des utilisateurs
        self.client_user = User.objects.create_user(
            username='client1',
            password='test123',
            role='client',
            email='client1@test.com'
        )
        self.producteur_user = User.objects.create_user(
            username='prod1',
            password='test123',
            role='producteur',
            email='prod1@test.com'
        )
        self.other_producteur = User.objects.create_user(
            username='prod2',
            password='test123',
            role='producteur',
            email='prod2@test.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='admin',
            email='admin@test.com'
        )

        # Création d'une catégorie
        self.category = Category.objects.create(nom="Fruits")

        # Création de produits
        self.prod1 = Product.objects.create(
            nom="Mangue",
            description="Mangue fraîche",
            prix=1000,
            stock=10,
            producteur=self.producteur_user,
            disponible=True
        )
        self.prod2 = Product.objects.create(
            nom="Banane",
            description="Banane plantain",
            prix=500,
            stock=5,
            producteur=self.producteur_user,
            disponible=True
        )
        self.prod3 = Product.objects.create(
            nom="Orange",
            description="Orange douce",
            prix=800,
            stock=0,
            producteur=self.other_producteur,
            disponible=False
        )

        # Création d'une commande pour les tests (par le client)
        self.order = Order.objects.create(
            client=self.client_user,
            notes="Test order",
            montant_total=0  # sera mis à jour après ajout des items
        )
        # Ajout d'items
        item1 = OrderItem.objects.create(
            commande=self.order,
            produit=self.prod1,
            quantite=2,
            prix_unitaire=self.prod1.prix
        )
        item2 = OrderItem.objects.create(
            commande=self.order,
            produit=self.prod2,
            quantite=1,
            prix_unitaire=self.prod2.prix
        )
        self.order.montant_total = item1.sous_total + item2.sous_total
        self.order.save()
        
        # Décrémenter le stock manuellement (car la commande a été créée directement, pas via le service)
        self.prod1.stock -= 2  # 10 - 2 = 8
        self.prod1.save()
        self.prod2.stock -= 1  # 5 - 1 = 4
        self.prod2.save()

        # Tokens JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        self.client_token = str(RefreshToken.for_user(self.client_user).access_token)
        self.producteur_token = str(RefreshToken.for_user(self.producteur_user).access_token)
        self.other_producteur_token = str(RefreshToken.for_user(self.other_producteur).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

        # URLs
        self.order_list_url = reverse('order-list')  # /commandes/
        self.order_detail_url = lambda pk: reverse('order-detail', args=[pk])
        self.order_cancel_url = lambda pk: reverse('order-annuler', args=[pk])  # via action
        self.order_update_status_url = lambda pk: reverse('order-update-status', args=[pk])

    # ---------- CRÉATION DE COMMANDE ----------
    def test_create_order_success(self):
        """Création d'une commande réussie par un client."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        data = {
            'items': [
                {'produit_id': self.prod1.id, 'quantite': 3},
                {'produit_id': self.prod2.id, 'quantite': 2}
            ],
            'notes': 'Livrer avant midi'
        }
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Vérifier que la commande a été créée
        self.assertEqual(Order.objects.count(), 2)  # une existante + nouvelle
        new_order = Order.objects.exclude(id=self.order.id).first()
        self.assertEqual(new_order.client, self.client_user)
        self.assertEqual(new_order.notes, 'Livrer avant midi')
        self.assertEqual(new_order.items.count(), 2)
        # Vérifier le stock décrémenté
        self.prod1.refresh_from_db()
        self.prod2.refresh_from_db()
        self.assertEqual(self.prod1.stock, 5)  # 8 (après setUp) - 3
        self.assertEqual(self.prod2.stock, 2)  # 4 (après setUp) - 2
        # Vérifier le montant total
        expected_total = 3*1000 + 2*500
        self.assertEqual(new_order.montant_total, expected_total)

    def test_create_order_unauthenticated(self):
        """Non authentifié ne peut pas créer de commande."""
        data = {'items': [{'produit_id': self.prod1.id, 'quantite': 1}]}
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_non_client(self):
        """Un producteur ne peut pas créer de commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        data = {'items': [{'produit_id': self.prod1.id, 'quantite': 1}]}
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # le service lève ValidationError
        self.assertIn('Seuls les clients peuvent passer commande', str(response.data))

    def test_create_order_empty_items(self):
        """Une commande sans produit est refusée."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        data = {'items': []}
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data)

    def test_create_order_insufficient_stock(self):
        """Stock insuffisant → erreur."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        data = {'items': [{'produit_id': self.prod1.id, 'quantite': 20}]}  # stock 10
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Stock insuffisant', str(response.data))

    def test_create_order_product_unavailable(self):
        """Produit indisponible → erreur."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        data = {'items': [{'produit_id': self.prod3.id, 'quantite': 1}]}  # disponible=False
        response = self.client.post(self.order_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('introuvable ou indisponible', str(response.data))

    # ---------- LISTE DES COMMANDES ----------
    def test_list_orders_as_client(self):
        """Un client ne voit que ses propres commandes."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # une seule commande
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_list_orders_as_producteur(self):
        """Un producteur voit les commandes contenant ses produits."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # la commande contient ses produits
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_list_orders_as_other_producteur(self):
        """Un producteur sans produits dans la commande ne voit rien."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_producteur_token}')
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_list_orders_as_admin(self):
        """L'admin voit toutes les commandes."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        response = self.client.get(self.order_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # une seule commande pour l'instant

    # ---------- DÉTAIL D'UNE COMMANDE ----------
    def test_retrieve_order_as_client(self):
        """Un client peut voir sa propre commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)

    def test_retrieve_order_as_other_client(self):
        """Un autre client ne peut pas voir la commande."""
        other_client = User.objects.create_user(username='client2', password='test', role='client')
        token = str(RefreshToken.for_user(other_client).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # car filtré par get_queryset

    def test_retrieve_order_as_producteur_concerned(self):
        """Un producteur concerné peut voir la commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_order_as_producteur_not_concerned(self):
        """Un producteur non concerné ne voit pas la commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.other_producteur_token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_order_as_admin(self):
        """L'admin peut voir n'importe quelle commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ---------- ANNULATION DE COMMANDE ----------
    def test_cancel_order_as_client(self):
        """Le client propriétaire peut annuler sa commande (si non expédiée)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        url = self.order_cancel_url(self.order.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.statut, Order.Status.ANNULEE)
        # Vérifier restitution du stock
        self.prod1.refresh_from_db()
        self.prod2.refresh_from_db()
        self.assertEqual(self.prod1.stock, 10)  # restitué
        self.assertEqual(self.prod2.stock, 5)

    def test_cancel_order_as_other_client(self):
        """Un autre client ne peut pas annuler la commande."""
        other_client = User.objects.create_user(username='client2', password='test', role='client')
        token = str(RefreshToken.for_user(other_client).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = self.order_cancel_url(self.order.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # filtré

    def test_cancel_order_as_producteur_concerned(self):
        """Un producteur concerné ne peut pas annuler (seul client ou admin)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.producteur_token}')
        url = self.order_cancel_url(self.order.id)
        response = self.client.post(url)
        # Il a accès à l'objet (car filtré), mais le service lève PermissionDenied → 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_order_as_admin(self):
        """L'admin peut annuler n'importe quelle commande."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = self.order_cancel_url(self.order.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.statut, Order.Status.ANNULEE)

    def test_cancel_order_already_shipped(self):
        """Impossible d'annuler une commande expédiée."""
        # Modifier le statut de la commande à EXPEDIEE
        self.order.statut = Order.Status.EXPEDIEE
        self.order.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        url = self.order_cancel_url(self.order.id)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Impossible d\'annuler une commande au statut', str(response.data))

    # ---------- MISE À JOUR DU STATUT (ADMIN) ----------
    def test_update_status_as_admin(self):
        """L'admin peut changer le statut (transition valide)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = self.order_update_status_url(self.order.id)
        data = {'statut': Order.Status.CONFIRMEE}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.statut, Order.Status.CONFIRMEE)

    def test_update_status_as_non_admin(self):
        """Un non-admin ne peut pas changer le statut."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.client_token}')
        url = self.order_update_status_url(self.order.id)
        data = {'statut': Order.Status.CONFIRMEE}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_status_invalid_transition(self):
        """Transition invalide → erreur."""
        self.order.statut = Order.Status.LIVREE
        self.order.save()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = self.order_update_status_url(self.order.id)
        data = {'statut': Order.Status.EN_ATTENTE}  # de LIVREE vers EN_ATTENTE impossible
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transition invalide', str(response.data))

    # ---------- PERMISSIONS D'OBJET AVEC LA CLASSE DE PERMISSION ----------
    # (Déjà testé via les accès, mais on peut ajouter un test explicite si besoin)

    # ---------- SUPPRESSION (non autorisée) ----------
    def test_delete_order_not_allowed(self):
        """La suppression directe n'est pas autorisée (renvoie 405)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        url = self.order_detail_url(self.order.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)