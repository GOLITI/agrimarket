# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer
from users.serializers import UserMinimalSerializer


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Serializer pour lire les items d'une commande."""
    produit = ProductSerializer(read_only=True)
    sous_total = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'produit', 'quantite', 'prix_unitaire', 'sous_total']


class OrderReadSerializer(serializers.ModelSerializer):
    """Serializer pour lire une commande complète."""
    items = OrderItemReadSerializer(many=True, read_only=True)
    client = UserMinimalSerializer(read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'client', 'statut', 'statut_display', 
            'montant_total', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'client', 'montant_total', 
            'created_at', 'updated_at'
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer pour créer un item de commande."""
    produit_id = serializers.IntegerField(min_value=1)
    quantite = serializers.IntegerField(min_value=1)

    def validate_quantite(self, value):
        if value < 1:
            raise serializers.ValidationError("La quantité doit être au moins 1.")
        return value


class OrderCreateSerializer(serializers.Serializer):
    """Serializer pour créer une nouvelle commande."""
    items = OrderItemCreateSerializer(many=True)
    notes = serializers.CharField(
        required=False, 
        allow_blank=True, 
        max_length=500
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Une commande doit contenir au moins un produit."
            )
        return value

    def create(self, validated_data):
        """Utilise le service OrderService pour créer la commande."""
        from .service import OrderService
        
        user = self.context['request'].user
        items_data = validated_data.get('items', [])
        notes = validated_data.get('notes', '')
        
        order = OrderService.create_order(
            client=user,
            items_data=items_data,
            notes=notes
        )
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'une commande (Admin uniquement)."""
    statut = serializers.ChoiceField(choices=Order.Status.choices)

    def validate_statut(self, value):
        if value not in dict(Order.Status.choices):
            raise serializers.ValidationError("Statut invalide.")
        return value
