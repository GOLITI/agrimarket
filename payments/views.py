# payments/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Payment
from .serializers import (
    PaymentSerializer, 
    PaymentCreateSerializer, 
    PaymentStatusUpdateSerializer
)
from .permissions import IsPaymentOwnerOrAdmin


@extend_schema_view(
    list=extend_schema(summary="Liste des paiements", tags=["Paiements"]),
    retrieve=extend_schema(summary="Détail d'un paiement", tags=["Paiements"]),
    create=extend_schema(summary="Créer un paiement", tags=["Paiements"]),
)
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les paiements.
    - Liste/Détail : accessible par le client propriétaire ou admin
    - Création : par le client propriétaire de la commande
    - Modification du statut : admin uniquement
    """
    queryset = Payment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPaymentOwnerOrAdmin]
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_queryset(self):
        """Filtre les paiements selon le rôle de l'utilisateur."""
        user = self.request.user
        
        if user.is_staff:
            return Payment.objects.all()
        
        # Les clients ne voient que leurs propres paiements
        if user.role == 'client':
            return Payment.objects.filter(commande__client=user)
        
        # Les producteurs voient les paiements des commandes contenant leurs produits
        if user.role == 'producteur':
            return Payment.objects.filter(
                commande__items__produit__producteur=user
            ).distinct()
        
        return Payment.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        if self.action == 'update_status':
            return PaymentStatusUpdateSerializer
        return PaymentSerializer
    
    @extend_schema(
        summary='Mettre à jour le statut du paiement (Admin)',
        request=PaymentStatusUpdateSerializer,
        responses={200: PaymentSerializer},
        tags=['Paiements'],
    )
    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[permissions.IsAdminUser]
    )
    def update_status(self, request, pk=None):
        """Mise à jour du statut d'un paiement (Admin uniquement)."""
        payment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment.statut = serializer.validated_data['statut']
        payment.save(update_fields=['statut'])
        
        read_serializer = PaymentSerializer(payment, context={'request': request})
        return Response(read_serializer.data)
