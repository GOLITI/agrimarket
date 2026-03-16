# payments/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPaymentOwnerOrAdmin(BasePermission):
    """
    Permission pour les paiements :
    - Un client ne peut voir que les paiements de ses propres commandes
    - Un producteur peut voir les paiements des commandes contenant ses produits
    - Un admin a tous les droits
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.is_staff:
            return True
        
        # Client propriétaire de la commande
        if request.user.role == 'client' and obj.commande.client == request.user:
            return True
        
        # Producteur concerné par la commande
        if request.user.role == 'producteur':
            return obj.commande.items.filter(
                produit__producteur=request.user
            ).exists()
        
        return False
