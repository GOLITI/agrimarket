# dashboard/services.py
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardService:
    """Service pour calculer les statistiques du tableau de bord."""
    
    @staticmethod
    def get_producteur_stats(producteur):
        """Calcule les statistiques pour un producteur."""
        from products.models import Product
        from orders.models import Order, OrderItem
        
        # Date du début du mois courant
        now = timezone.now()
        debut_mois = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
        
        # Produits du producteur
        produits = Product.objects.filter(producteur=producteur)
        nombre_produits = produits.count()
        produits_disponibles = produits.filter(disponible=True).count()
        produits_rupture_stock = produits.filter(stock=0).count()
        
        # Commandes contenant les produits du producteur
        order_items = OrderItem.objects.filter(
            produit__producteur=producteur
        ).select_related('commande')
        
        # Nombre de commandes distinctes
        commandes = Order.objects.filter(
            items__produit__producteur=producteur
        ).distinct()
        nombre_commandes = commandes.count()
        
        # Revenus (somme des sous-totaux des items du producteur)
        revenus_total = order_items.exclude(
            commande__statut=Order.Status.ANNULEE
        ).aggregate(
            total=Sum('quantite') * Sum('prix_unitaire')
        )['total'] or 0
        
        # Calcul plus précis des revenus
        revenus_total = sum(
            item.sous_total for item in order_items.exclude(
                commande__statut=Order.Status.ANNULEE
            )
        )
        
        revenus_mois_courant = sum(
            item.sous_total for item in order_items.filter(
                commande__created_at__gte=debut_mois
            ).exclude(commande__statut=Order.Status.ANNULEE)
        )
        
        # Statuts des commandes
        commandes_en_attente = commandes.filter(
            statut=Order.Status.EN_ATTENTE
        ).count()
        
        commandes_livrees = commandes.filter(
            statut=Order.Status.LIVREE
        ).count()
        
        return {
            'nombre_produits': nombre_produits,
            'nombre_commandes': nombre_commandes,
            'revenus_total': revenus_total,
            'revenus_mois_courant': revenus_mois_courant,
            'produits_disponibles': produits_disponibles,
            'produits_rupture_stock': produits_rupture_stock,
            'commandes_en_attente': commandes_en_attente,
            'commandes_livrees': commandes_livrees,
        }
    
    @staticmethod
    def get_admin_stats():
        """Calcule les statistiques globales pour l'administrateur."""
        from products.models import Product
        from orders.models import Order, OrderItem
        
        # Date du début du mois courant
        now = timezone.now()
        debut_mois = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
        
        # Utilisateurs
        nombre_utilisateurs = User.objects.count()
        nombre_clients = User.objects.filter(role='client').count()
        nombre_producteurs = User.objects.filter(role='producteur').count()
        
        # Produits
        nombre_produits = Product.objects.count()
        
        # Commandes
        commandes = Order.objects.all()
        nombre_commandes = commandes.count()
        
        # Revenus (total des commandes non annulées)
        revenus_total = commandes.exclude(
            statut=Order.Status.ANNULEE
        ).aggregate(total=Sum('montant_total'))['total'] or 0
        
        revenus_mois_courant = commandes.filter(
            created_at__gte=debut_mois
        ).exclude(
            statut=Order.Status.ANNULEE
        ).aggregate(total=Sum('montant_total'))['total'] or 0
        
        # Statuts des commandes
        commandes_en_attente = commandes.filter(
            statut=Order.Status.EN_ATTENTE
        ).count()
        
        commandes_confirmees = commandes.filter(
            statut=Order.Status.CONFIRMEE
        ).count()
        
        commandes_expediees = commandes.filter(
            statut=Order.Status.EXPEDIEE
        ).count()
        
        commandes_livrees = commandes.filter(
            statut=Order.Status.LIVREE
        ).count()
        
        commandes_annulees = commandes.filter(
            statut=Order.Status.ANNULEE
        ).count()
        
        return {
            'nombre_utilisateurs': nombre_utilisateurs,
            'nombre_clients': nombre_clients,
            'nombre_producteurs': nombre_producteurs,
            'nombre_produits': nombre_produits,
            'nombre_commandes': nombre_commandes,
            'revenus_total': revenus_total,
            'revenus_mois_courant': revenus_mois_courant,
            'commandes_en_attente': commandes_en_attente,
            'commandes_confirmees': commandes_confirmees,
            'commandes_expediees': commandes_expediees,
            'commandes_livrees': commandes_livrees,
            'commandes_annulees': commandes_annulees,
        }
