# payments/serializers.py
from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderReadSerializer


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les paiements."""
    commande = OrderReadSerializer(read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    methode_display = serializers.CharField(source='get_methode_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'commande', 'montant', 'methode', 'methode_display',
            'statut', 'statut_display', 'reference_transaction',
            'notes', 'created_at', 'updated_at', 'est_complete'
        ]
        read_only_fields = [
            'id', 'commande', 'montant', 'created_at', 
            'updated_at', 'est_complete'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un paiement."""
    commande_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'commande_id', 'methode', 'reference_transaction', 'notes'
        ]
    
    def validate_commande_id(self, value):
        """Vérifie que la commande existe et n'a pas déjà de paiement."""
        from orders.models import Order
        
        try:
            commande = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Commande introuvable.")
        
        if hasattr(commande, 'paiement'):
            raise serializers.ValidationError(
                "Cette commande a déjà un paiement associé."
            )
        
        return value
    
    def create(self, validated_data):
        """Crée le paiement avec le montant de la commande."""
        from orders.models import Order
        
        commande_id = validated_data.pop('commande_id')
        commande = Order.objects.get(id=commande_id)
        
        payment = Payment.objects.create(
            commande=commande,
            montant=commande.montant_total,
            **validated_data
        )
        return payment


class PaymentStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'un paiement."""
    statut = serializers.ChoiceField(choices=Payment.Status.choices)
    
    def validate_statut(self, value):
        if value not in dict(Payment.Status.choices):
            raise serializers.ValidationError("Statut invalide.")
        return value
