# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from .services import DashboardService
from .serializers import ProducteurStatsSerializer, AdminStatsSerializer


class ProducteurDashboardView(APIView):
    """
    Tableau de bord pour les producteurs.
    Affiche les statistiques de leurs produits et commandes.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary='Tableau de bord producteur',
        description='Statistiques pour le producteur connecté : produits, commandes, revenus',
        responses={200: ProducteurStatsSerializer},
        tags=['Dashboard'],
    )
    def get(self, request):
        """Récupère les statistiques du producteur connecté."""
        user = request.user
        
        # Vérifier que l'utilisateur est bien un producteur
        if not user.is_producteur():
            return Response(
                {'detail': 'Seuls les producteurs peuvent accéder à ce tableau de bord.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = DashboardService.get_producteur_stats(user)
        serializer = ProducteurStatsSerializer(stats)
        return Response(serializer.data)


class AdminDashboardView(APIView):
    """
    Tableau de bord pour les administrateurs.
    Affiche les statistiques globales de la plateforme.
    """
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        summary='Tableau de bord administrateur',
        description='Statistiques globales : utilisateurs, produits, commandes, revenus',
        responses={200: AdminStatsSerializer},
        tags=['Dashboard'],
    )
    def get(self, request):
        """Récupère les statistiques globales."""
        stats = DashboardService.get_admin_stats()
        serializer = AdminStatsSerializer(stats)
        return Response(serializer.data)
