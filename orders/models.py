from django.conf import settings
from django.db import models

class Order(models.Model):
    class Status(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente'
        CONFIRMEE  = 'confirmee',  'Confirmée'
        EXPEDIEE   = 'expediee',   'Expédiée'
        LIVREE     = 'livree',     'Livrée'
        ANNULEE    = 'annulee',    'Annulée'

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='commandes',
    )
    statut = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE,
    )
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'commande'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'statut']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'Commande #{self.id} — {self.client.username} ({self.get_statut_display()})'

    @property
    def peut_etre_annulee(self):
        return self.statut not in [self.Status.EXPEDIEE, self.Status.LIVREE, self.Status.ANNULEE]


class OrderItem(models.Model):
    commande = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot du prix

    class Meta:
        indexes = [models.Index(fields=['commande', 'produit'])]
        # Empêcher la duplication du même produit dans une commande (optionnel)
        unique_together = ['commande', 'produit']

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f'{self.quantite}x {self.produit.nom} @ {self.prix_unitaire}'