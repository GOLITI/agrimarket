from django.db import transaction, models
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Order, OrderItem
from products.models import Product


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(client, items_data, notes=''):
        """
        Crée une commande et décrémente le stock de façon atomique.
        - client : instance de User (doit être de rôle 'client')
        - items_data : liste de dict [{'produit_id': int, 'quantite': int}, ...]
        - notes : str optionnelle
        Retourne l'objet Order créé.
        """
        if client.role != 'client':
            raise ValidationError("Seuls les clients peuvent passer commande.")

        if not items_data:
            raise ValidationError('Une commande doit contenir au moins un produit.')

        order = Order.objects.create(client=client, notes=notes)
        total = 0

        # Récupérer tous les produits avec verrouillage pour éviter les race conditions
        produit_ids = [item['produit_id'] for item in items_data]
        produits = {
            p.id: p
            for p in Product.objects.select_for_update().filter(
                id__in=produit_ids, disponible=True
            )
        }

        for item_data in items_data:
            produit = produits.get(item_data['produit_id'])
            if not produit:
                raise ValidationError(
                    f'Le produit #{item_data["produit_id"]} est introuvable ou indisponible.'
                )

            quantite = item_data['quantite']

            if produit.stock < quantite:
                raise ValidationError(
                    f'Stock insuffisant pour « {produit.nom} » : '
                    f'{produit.stock} disponible(s), {quantite} demandé(s).'
                )

            # Décrémentation du stock
            produit.stock -= quantite
            if produit.stock == 0:
                produit.disponible = False
            produit.save(update_fields=['stock', 'disponible'])

            # Snapshot du prix
            prix_unitaire = produit.prix
            OrderItem.objects.create(
                commande=order,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire,
            )
            total += prix_unitaire * quantite

        order.montant_total = total
        order.save(update_fields=['montant_total'])
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order, user):
        """
        Annule une commande et restitue le stock.
        - user : utilisateur faisant la demande (doit être le client ou admin)
        Interdit si la commande est déjà expédiée ou livrée.
        """
        # Vérification des droits
        if user != order.client and not user.is_staff:
            raise PermissionDenied("Vous n'êtes pas autorisé à annuler cette commande.")

        if not order.peut_etre_annulee:
            raise ValidationError(
                f'Impossible d\'annuler une commande au statut « {order.get_statut_display()} ».'
            )

        # Restitution atomique du stock
        for item in order.items.select_related('produit'):
            # Vérifier que le produit existe encore (normalement oui grâce à PROTECT)
            Product.objects.filter(id=item.produit_id).update(
                stock=models.F('stock') + item.quantite,
                disponible=True,
            )

        order.statut = Order.Status.ANNULEE
        order.save(update_fields=['statut'])
        return order

    @staticmethod
    @transaction.atomic
    def update_status(order, new_status, user):
        """
        Met à jour le statut d'une commande.
        - user : utilisateur (doit être admin)
        - new_status : valeur du statut (chaîne)
        Valide les transitions autorisées.
        """
        if not user.is_staff:
            raise PermissionDenied("Seul l'administrateur peut changer le statut d'une commande.")

        TRANSITIONS = {
            Order.Status.EN_ATTENTE: [Order.Status.CONFIRMEE, Order.Status.ANNULEE],
            Order.Status.CONFIRMEE:  [Order.Status.EXPEDIEE, Order.Status.ANNULEE],
            Order.Status.EXPEDIEE:   [Order.Status.LIVREE],
            Order.Status.LIVREE:     [],
            Order.Status.ANNULEE:    [],
        }

        allowed = TRANSITIONS.get(order.statut, [])
        if new_status not in allowed:
            raise ValidationError(
                f'Transition invalide : {order.get_statut_display()} → {Order.Status(new_status).label}'
            )

        order.statut = new_status
        order.save(update_fields=['statut'])
        return order