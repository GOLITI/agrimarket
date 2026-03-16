# products/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsProducteurOrReadOnly(BasePermission):
    """
    Lecture publique. Écriture réservée aux producteurs.
    Modification/suppression réservée au producteur propriétaire ou à l'admin.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        # Pour la création, seul un producteur peut le faire (pas l'admin)
        if request.method == 'POST':
            return request.user.is_producteur()
        # Pour les autres actions (PUT, PATCH, DELETE), on laisse has_object_permission décider
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # L'admin peut tout modifier
        if request.user.is_staff:
            return True
        # Sinon, il faut être le producteur propriétaire
        return obj.producteur == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Permission pour les catégories :
    - Lecture : publique.
    - Écriture (POST, PUT, PATCH, DELETE) : réservée aux administrateurs.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff