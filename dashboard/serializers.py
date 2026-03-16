# dashboard/serializers.py
from rest_framework import serializers


class ProducteurStatsSerializer(serializers.Serializer):
    """Statistiques pour un producteur."""
    nombre_produits = serializers.IntegerField()
    nombre_commandes = serializers.IntegerField()
    revenus_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenus_mois_courant = serializers.DecimalField(max_digits=12, decimal_places=2)
    produits_disponibles = serializers.IntegerField()
    produits_rupture_stock = serializers.IntegerField()
    commandes_en_attente = serializers.IntegerField()
    commandes_livrees = serializers.IntegerField()


class AdminStatsSerializer(serializers.Serializer):
    """Statistiques globales pour l'administrateur."""
    nombre_utilisateurs = serializers.IntegerField()
    nombre_clients = serializers.IntegerField()
    nombre_producteurs = serializers.IntegerField()
    nombre_produits = serializers.IntegerField()
    nombre_commandes = serializers.IntegerField()
    revenus_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenus_mois_courant = serializers.DecimalField(max_digits=12, decimal_places=2)
    commandes_en_attente = serializers.IntegerField()
    commandes_confirmees = serializers.IntegerField()
    commandes_expediees = serializers.IntegerField()
    commandes_livrees = serializers.IntegerField()
    commandes_annulees = serializers.IntegerField()
