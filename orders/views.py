# orders/views.py
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError, PermissionDenied as DRFPermissionDenied
from drf_spectacular.utils import extend_schema
from .permissions import IsClientOwnerOrAdmin

from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer, OrderStatusUpdateSerializer
from .service import OrderService


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    permission_classes = [permissions.IsAuthenticated, IsClientOwnerOrAdmin]

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items__produit').select_related('client')
        user = self.request.user

        if user.is_staff:
            return qs
        if user.role == 'client':
            return qs.filter(client=user)
        if user.role == 'producteur':
            # Commandes contenant au moins un produit de ce producteur
            return qs.filter(items__produit__producteur=user).distinct()
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderReadSerializer

    @extend_schema(summary='Lister mes commandes', tags=['Commandes'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Passer une commande',
        request=OrderCreateSerializer,
        responses={201: OrderReadSerializer},
        tags=['Commandes'],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = serializer.save()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)
        read_serializer = OrderReadSerializer(order, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary='Détail d\'une commande', tags=['Commandes'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(summary='Annuler une commande', tags=['Commandes'])
    @action(detail=True, methods=['post'], url_path='annuler')
    def annuler(self, request, pk=None):
        order = self.get_object()
        try:
            order = OrderService.cancel_order(order, request.user)
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        except DjangoPermissionDenied as e:
            raise DRFPermissionDenied(str(e))
        read_serializer = OrderReadSerializer(order, context={'request': request})
        return Response(read_serializer.data)

    @extend_schema(
        summary='Changer le statut (Admin)',
        request=OrderStatusUpdateSerializer,
        responses={200: OrderReadSerializer},
        tags=['Commandes'],
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = OrderService.update_status(
                order, serializer.validated_data['statut'], request.user
            )
        except DjangoValidationError as e:
            raise DRFValidationError(e.messages)
        except DjangoPermissionDenied as e:
            raise DRFPermissionDenied(str(e))
        read_serializer = OrderReadSerializer(order, context={'request': request})
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Suppression non autorisée. Utilisez l\'annulation.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )