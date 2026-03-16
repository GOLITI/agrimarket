# orders/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsClientOwnerOrAdmin(BasePermission):
    """
    Permission pour les commandes :
    - Un client ne peut voir/modifier que ses propres commandes.
    - Un producteur peut voir les commandes contenant ses produits.
    - Un admin a tous les droits.
    """
    def has_permission(self, request, view):
        # Authentifié requis pour toute action
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.is_staff:
            return True

        # Client propriétaire de la commande
        if request.user.role == 'client' and obj.client == request.user:
            return True

        # Producteur : vérifie si au moins un produit de la commande lui appartient
        if request.user.role == 'producteur':
            # Optimisation : utiliser une requête plutôt que de charger tous les items
            return obj.items.filter(produit__producteur=request.user).exists()

        return False