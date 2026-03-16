from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    """L'utilisateur ne peut modifier que son propre profil."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS: 
            return True
        return obj == request.user or request.user.is_staff 
