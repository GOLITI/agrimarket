from django.db import models
from django.conf import settings
from orders.models import Order


class Payment(models.Model):
    """Modèle pour les paiements des commandes."""
    
    class Status(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        REUSSIE = 'reussie', 'Réussie'
        ECHOUEE = 'echouee', 'Échouée'
        REMBOURSEE = 'remboursee', 'Remboursée'
    
    class Method(models.TextChoices):
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        CARTE_BANCAIRE = 'carte_bancaire', 'Carte Bancaire'
        ESPECES = 'especes', 'Espèces'
        VIREMENT = 'virement', 'Virement Bancaire'
    
    commande = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='paiement'
    )
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    methode = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.MOBILE_MONEY
    )
    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE
    )
    reference_transaction = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Référence externe de la transaction (ex: ID Mobile Money)"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'paiement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['commande', 'statut']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f'Paiement #{self.id} — Commande #{self.commande.id} ({self.get_statut_display()})'
    
    @property
    def est_complete(self):
        """Vérifie si le paiement est terminé avec succès."""
        return self.statut == self.Status.REUSSIE
