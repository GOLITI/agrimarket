from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdminOrReadOnly, IsProducteurOrReadOnly


@extend_schema_view(
    list=extend_schema(summary="Liste des catégories", tags=["Catégories"]),
    retrieve=extend_schema(summary="Détail d'une catégorie", tags=["Catégories"]),
    create=extend_schema(summary="Créer une catégorie (admin)", tags=["Catégories"]),
    update=extend_schema(summary="Mettre à jour une catégorie (admin)", tags=["Catégories"]),
    partial_update=extend_schema(summary="Modifier partiellement une catégorie (admin)", tags=["Catégories"]),
    destroy=extend_schema(summary="Supprimer une catégorie (admin)", tags=["Catégories"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les catégories.
    - Lecture publique (tout le monde peut voir)
    - Écriture réservée aux administrateurs
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=extend_schema(summary="Liste des produits", tags=["Produits"]),
    retrieve=extend_schema(summary="Détail d'un produit", tags=["Produits"]),
    create=extend_schema(
        summary="Créer un produit (producteur)",
        description="Seuls les producteurs authentifiés peuvent créer un produit.",
        tags=["Produits"]
    ),
    update=extend_schema(
        summary="Mettre à jour un produit (propriétaire)",
        description="Seul le producteur propriétaire peut modifier le produit.",
        tags=["Produits"]
    ),
    partial_update=extend_schema(
        summary="Modifier partiellement un produit (propriétaire)",
        tags=["Produits"]
    ),
    destroy=extend_schema(
        summary="Supprimer un produit (propriétaire)",
        tags=["Produits"]
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les produits.
    - Lecture : publique
    - Création : réservée aux producteurs authentifiés
    - Modification/Suppression : réservée au producteur propriétaire
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProducteurOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categories', 'producteur', 'disponible', 'unite']
    search_fields = ['nom', 'description']
    ordering_fields = ['prix', 'created_at', 'stock']
    ordering = ['-created_at']  # tri par défaut : du plus récent au plus ancien

    def perform_create(self, serializer):
        """
        Associe automatiquement le producteur connecté au produit créé.
        """
        serializer.save(producteur=self.request.user)

    # Exemple d'action personnalisée : lister les produits du producteur connecté
    @action(detail=False, methods=['get'], url_path='mes-produits')
    def mes_produits(self, request):
        """
        Retourne les produits du producteur connecté.
        """
        if not request.user.is_authenticated or not request.user.is_producteur():
            return Response(
                {"detail": "Authentification de producteur requise."},
                status=status.HTTP_403_FORBIDDEN
            )
        produits = self.get_queryset().filter(producteur=request.user)
        page = self.paginate_queryset(produits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(produits, many=True)
        return Response(serializer.data)

    # On peut surcharger get_queryset pour filtrer par défaut (par ex. produits disponibles)
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     if not self.request.user.is_staff:
    #         # Les non-admins ne voient que les produits disponibles
    #         queryset = queryset.filter(disponible=True)
    #     return queryset